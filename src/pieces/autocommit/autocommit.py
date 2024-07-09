from collections import defaultdict 
from pieces_os_client.models.seeds import Seeds
from pieces_os_client.models.seed import Seed
from pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum
from pieces_os_client.models.seeded_asset import SeededAsset
from pieces_os_client.models.seeded_format import SeededFormat
from pieces_os_client.models.seeded_fragment import SeededFragment
from pieces_os_client.models.transferable_string import TransferableString
from pieces_os_client.models.seeded_asset_metadata import SeededAssetMetadata
from pieces_os_client.models.anchor_type_enum import AnchorTypeEnum
from pieces_os_client.models.seeded_anchor import SeededAnchor
def get_current_working_changes() -> Optional[Tuple[str,list]]:
            List of seeded asset to be input to the relevence
        show_error("No changes found","Please make sure you have added some files to your staging area")
        return 
    content_file = defaultdict(str)  # {file path : changes of the file}
        if (line.startswith('+') and not line.startswith('+++')) or (line.startswith('-') and not line.startswith('---')):
            
            content_file[os.path.join(os.getcwd(),*file_name.split("/"))] += line.strip()

    return summary,Seeds(iterable=[
        create_seeded_asset(file_path,content) for file_path,content in content_file.items()
    ]) # Create seed for each new file
def create_seeded_asset(file_path:str,content:str) -> Seed:
    return Seed(
			asset=SeededAsset(
				application=Settings.application,
				format=SeededFormat(
					fragment=SeededFragment(
						string=TransferableString(raw=content)
					)
				),
				metadata=SeededAssetMetadata(
                    anchors=[
                        SeededAnchor(
                            fullpath=file_path,
                            type=AnchorTypeEnum.FILE
                        )
                    ]
                )
			),
			type="SEEDED_ASSET"
		)

    

        changes_summary,seeds = get_current_working_changes()
    except TypeError:
    commit_message = get_commit_message(changes_summary,seeds)
    if not commit_message: # Error in the commit message
    if issue_flag:
        try:
            issue_number,issue_title,issue_markdown = get_issue_details(seeds)
        except TypeError: # Returned none 
            issue_flag = False
            # Print the issues if we cant find the issie
            if issue_number == None and issue_markdown:
                md = Markdown(issue_markdown)
                        break

def get_issue_details(seeds):
    issue_prompt = """Please provide the issue number that is related to the changes, If nothing related write 'None'.
            `Output format WITHOUT ADDING ANYTHING ELSE: "Issue: **ISSUE NUMBER OR NONE HERE**`,
            `Example: 'Issue: 12', 'Issue: None'`,
            `Note: Don't provide any other information`
            `Here are the issues:`\n{issues}"""
    
    # Issues
    repo_details = get_git_repo_name()
    issues = get_repo_issues(*repo_details) if repo_details else [] # Check if we got a vaild repo name

    if issues:
        try:
            # Make the issues look nicer
            issue_markdown = [
                f"- `Issue_number: {issue['number']}`\n- `Title: {issue['title']}`\n- `Body: {issue['body']}`"
                for issue in issues
            ]
            issue_markdown = "\n".join(issue_markdown) # To string
            issue_number = QGPTApi(Settings.api_client).relevance(
                    QGPTRelevanceInput(
                        query=issue_prompt.format(issues=issue_markdown),
                        application=Settings.application.id,
                        model=Settings.model_id,
                        options=QGPTRelevanceInputOptions(question=True),
                        seeds=seeds
                    )).answer.answers.iterable[0].text
    
            
            # Extract the issue part
            issue_number = issue_number.replace("Issue: ", "") 
            # If the issue is a number 
            issue_number = int(issue_number)
            issue_title = next((issue["title"] for issue in issues if issue["number"] == issue_number), None)
        except: 
            issue_number = None
            issue_title = ""
        return issue_number,issue_title,issue_markdown
    

def get_commit_message(changes_summary,seeds):
    message_prompt = f"""Act as a git expert developer to generate a concise git commit message **using best git commit message practices** to follow these specifications:
                `Message language: English`,
                `Format of the message: "(task done): small description"`,
                `task done can be one from: "feat,fix,chore,refactor,docs,style,test,perf,ci,build,revert"`,
                `Example of the message: "docs: add new guide on python"`,
                Your response should be: `__The message is: **YOUR COMMIT MESSAGE HERE**__` WITHOUT ADDING ANYTHING ELSE",
                `Here are the changes summary:`\n{changes_summary}`
                The actual code changes provide to you in the seeds,
                `The changed parts is provided in the context where if the line start with "+"  means that line is added or "-" if it is removed"""


    try:
        commit_message = QGPTApi(Settings.api_client).relevance(
            QGPTRelevanceInput(
                query=message_prompt,
                seeds=seeds,
                application=Settings.application.id,
                model=Settings.model_id,
                options=QGPTRelevanceInputOptions(question=True)
            )).answer.answers.iterable[0].text 
        
        # Remove extras from the commit message
        commit_message = commit_message.replace("The message is:","",1) # Remove the "message is" part as mentioned in the prompt
        commit_message = commit_message.replace('*', '') # Remove the bold and italic characters
        commit_message = commit_message.replace('__', '') # Remove the bold and italic characters
        # Remove leading and trailing whitespace
        commit_message = commit_message.strip()
    except Exception as e:
        print("Error in getting the commit message",e)
        return
    return commit_message