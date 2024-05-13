from pieces.settings import Settings
from pieces.gui import show_error
from typing import Dict,Optional
import json
import queue
import threading

from pieces_os_client.api.assets_api import AssetsApi
from pieces_os_client.api.asset_api import AssetApi
from pieces_os_client.api.format_api import FormatApi
from pieces_os_client.api.shares_api import SharesApi
from pieces_os_client.api.distributions_api import DistributionsApi
from pieces_os_client.api.user_api import UserApi
from pieces_os_client.api.linkify_api import LinkifyApi

from pieces_os_client.models.seed import Seed
from pieces_os_client.models.seeded_asset import SeededAsset
from pieces_os_client.models.seeded_format import SeededFormat
from pieces_os_client.models.seeded_fragment import SeededFragment
from pieces_os_client.models.seeded_share import SeededShare
from pieces_os_client.models.seeded_distribution import SeededDistribution
from pieces_os_client.models.seeded_git_hub_distribution import SeededGitHubDistribution
from pieces_os_client.models.seeded_git_hub_gist_distribution import SeededGitHubGistDistribution
from pieces_os_client.models.transferable_string import TransferableString
from pieces_os_client.models.classification_generic_enum import ClassificationGenericEnum
from pieces_os_client.models.asset_reclassification import AssetReclassification
from pieces_os_client.models.asset import Asset
from pieces_os_client.models.format import Format
from pieces_os_client.models.streamed_identifiers import StreamedIdentifiers
from pieces_os_client.models.linkify import Linkify



class AssetsCommandsApi:
	assets_snapshot: Dict[str, Optional[Asset]] = {} # should be filled in the run in loop
	asset_queue = queue.Queue() # Queue for asset_ids to be processed
	block = True # to wait for the queue to recevive the first asset id
	asset_set = set()  # Set for asset_ids in the queue

	@staticmethod
	def create_new_asset(raw_string, metadata=None):
		assets_api = AssetsApi(Settings.api_client)

		# Construct a Seed
		seed = Seed(
			asset=SeededAsset(
				application=Settings.application,
				format=SeededFormat(
					fragment=SeededFragment(
						string=TransferableString(raw=raw_string)
					)
				),
				metadata=metadata  # This should be constructed as per the SDK's definition
			),
			type="SEEDED_ASSET"
		)
		
		# Creating the new asset using the assets API
		created_asset = assets_api.assets_create_new_asset(transferables=False, seed=seed)
		return created_asset
	
	@classmethod
	def get_assets_snapshot(cls) -> Dict[str, Optional[Asset]]:
		"""
		Get all the assets that where cached into memory before. 
		If no assets cached yet it will return a dict of all the assets_ids with the None value

		:return: Dict[str, Optional[Asset]]
		""" 

		if cls.assets_snapshot:
			return cls.assets_snapshot
	

		assets_api = AssetsApi(Settings.api_client)
		# Call the API to get assets identifiers
		api_response = assets_api.assets_identifiers_snapshot()

		# Extract the 'id' values from each item in the 'iterable' list
		cls.assets_snapshot = {item.id:None for item in api_response.iterable}

		return cls.assets_snapshot
		
	@classmethod
	def update_asset_snapshot(cls,asset_id):
		asset_api = AssetApi(Settings.api_client)
		asset = asset_api.asset_snapshot(asset_id)
		cls.assets_snapshot[asset_id] = asset # Cache the asset
		return asset

	@classmethod
	def worker(cls):
		try:
			while True:
				asset_id = cls.asset_queue.get(block=cls.block,timeout=5)
				cls.asset_set.remove(asset_id)  # Remove asset_id from the set
				cls.update_asset_snapshot(asset_id)
				cls.asset_queue.task_done()
		except queue.Empty: # queue is empty and the block is false
			if cls.block:
				cls.worker() # if there is more assets to load
			return # End the worker
	
	@classmethod
	def assets_snapshot_callback(cls,ids:StreamedIdentifiers):
		# Start the worker thread if it's not running
		threading.Thread(target = cls.worker).start()
		cls.block = True
		for item in ids.iterable:
			asset_id = item.asset.id
			if asset_id not in cls.assets_snapshot:
				cls.assets_snapshot[asset_id] = None
			
			if asset_id not in cls.asset_set:
				if item.deleted:
					cls.assets_snapshot.pop(asset_id)
				else:
					cls.asset_queue.put(asset_id)  # Add asset_id to the queue
					cls.asset_set.add(asset_id)  # Add asset_id to the set
		cls.block = False # Remove the block to end the thread



	@classmethod
	def get_asset_snapshot(cls,asset_id:str) -> Asset:
		"""Get the asset snapshot from the cache if found if not it will update the cache and return the snapshot"""
		asset = cls.assets_snapshot.get(asset_id)
		if asset:
			return asset
		else:
			return cls.update_asset_snapshot(asset_id)

	

	@classmethod
	def edit_asset_name(cls,asset_id, new_name):
		asset_api = AssetApi(Settings.api_client)

		# Get the asset using the provided asset_id
		asset = cls.get_asset_snapshot(asset_id)

		# Check if the existing name is found and update it
		existing_name = asset.name
		asset.name = new_name

		# Update the asset using the API
		try:
			asset_api.asset_update(asset=asset, transferables=False)
			print(f"Asset name changed from '{existing_name}' to '{new_name}'")
		except Exception as e:
			show_error("Error updating asset: ",{e})


	@staticmethod
	def delete_asset_by_id(asset_id):
		delete_instance = AssetsApi(Settings.api_client)

		try:
			response = delete_instance.assets_delete_asset(asset_id)
			return response
		except Exception as e:
			return f"Failed to delete {asset_id}"

	@staticmethod
	def reclassify_asset(asset_id, classification):
		asset_api = AssetApi(Settings.api_client)
		with open(Settings.extensions_dir) as f:
			extension_mapping = json.load(f)
			if classification not in extension_mapping:
				show_error(f"Invalid classification: {classification}","Please choose from the following: \n "+", ".join(extension_mapping.keys()))
				return
			
		try:
			asset = asset_api.asset_snapshot(asset_id)
			if asset.original.reference.classification.generic == ClassificationGenericEnum.IMAGE:
				show_error("Error in reclassify asset","Image original format is not supported")
				return
			asset_api.asset_reclassify(asset_reclassification=AssetReclassification(ext=classification,asset=asset),
												transferables=False)
			print(f"reclassify {asset.name} the asset to {classification} successfully")
		except Exception as e:
			show_error("Error reclassifying asset: ",{e})

	@staticmethod
	def update_asset_value(file_path,asset_id):
		try:
			with open(file_path,"r") as f:
				data = f.read()
		except FileNotFoundError:
			show_error("Error in update asset","File not found")
			return
		asset_api = AssetApi(Settings.api_client)
		format_api = FormatApi(Settings.api_client)

		# get asset
		created = asset_api.asset_snapshot(asset_id, transferables=False)

		# update the original format's value
		original = format_api.format_snapshot(created.original.id, transferable=True)
		if original.classification.generic == ClassificationGenericEnum.IMAGE:
			show_error("Error in update asset","Original format is not supported")
			return
		if original.fragment and original.fragment.string and original.fragment.string.raw:
			original.fragment.string.raw = data
		elif original.file and original.file.string and original.file.string.raw:
			original.file.string.raw = data
		else:
			# check if the string value is not empty
			show_error("Error in update asset","Original value is empty")
			return

		format_api.format_update_value(transferable=False, format=original)

		print(f"{created.name} updated successfully.")

	def extract_asset_info(data:Asset) -> dict:
		"""
		Return some info about the asset
		:param data: The data containing information about the asset
		:return: A dictionary containing the asset's name, date created, date updated, type, language, and raw code snippet
		"""

		name = data.name if data.name else "New Asset"
		created_readable = data.created.readable if data.created.readable else "Unknown"
		updated_readable = data.updated.readable if data.updated.readable else "Unknown"
		type = "No Type"
		language = "No Language"
		raw = None  # Initialize raw code snippet as None
		iterable = data.formats.iterable
		if iterable:
			original:Format = [format for format in iterable if format.id == data.original.id][0]
			if original:
				type = original.classification.generic.value
				language = original.classification.specific.value
				
				if original.fragment:
					raw = original.fragment.string.raw
				elif original.file.string:
					raw = original.file.string.raw
				elif original.file.bytes:
					raw = original.file.bytes.raw
				
		return {"name":name,
				"created_at":created_readable,
				'updated_at': updated_readable,
				"type" :type,
				"language": language,
				"raw": raw}

	@classmethod
	def generate_shareable_link(cls,asset:Asset,async_req=True):
		user = UserApi(Settings.api_client).user_snapshot().user
		return LinkifyApi(Settings.api_client).linkify(async_req=async_req,linkify=Linkify(asset=asset,access="PUBLIC",user=user))


	@classmethod
	def delete_shareable_link(cls,share_id):
		return LinkifyApi(Settings.api_client).linkify_share_revoke(share=share_id)


	@classmethod
	def create_gist(cls,name:str,description:str,public:bool):
		return DistributionsApi(Settings.api_client).distributions_create_new_distribution(
			seeded_distribution = SeededDistribution(
				github=SeededGitHubDistribution(
					gist=SeededGitHubGistDistribution(
						name=name,
						description=description,
						public=public
					)
				)
			) 
		)
    	
