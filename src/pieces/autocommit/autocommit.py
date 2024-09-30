from typing import TYPE_CHECKING, Optional,Tuple
if TYPE_CHECKING:
    from pieces_os_client.models.seeds import Seeds
def get_current_working_changes() -> Optional[Tuple[str, "Seeds"]]:
            List of seeded asset to be input to the relevance
    from pieces_os_client.models.seed import Seed
    from pieces_os_client.models.seeds import Seeds
    from pieces_os_client.models.seeded_asset import SeededAsset
    from pieces_os_client.models.seeded_asset_metadata import SeededAssetMetadata
    from pieces_os_client.models.seeded_format import SeededFormat
    from pieces_os_client.models.seeded_fragment import SeededFragment
    from pieces_os_client.models.transferable_string import TransferableString
    from pieces_os_client.models.anchor_type_enum import AnchorTypeEnum
    from pieces_os_client.models.seeded_anchor import SeededAnchor
    try:
        result = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
        if not result.stdout.strip():
            show_error("No changes found", "Please make sure you have added some files to your staging area")
            return None
        
        detailed_diff = result.stdout.strip()
        summary = ""
        content_file = defaultdict(str)
        lines_diff = detailed_diff.split("\n")

        for idx, line in enumerate(lines_diff):
            if line.startswith('diff --git'):
                file_changed = re.search(r'diff --git a/(.+) b/\1', line)
                if file_changed:
                    file_name = file_changed.group(1)
                    if lines_diff[idx + 1] == "new file mode 100644":
                        summary += f"File created: **{file_name}**\n"
                    elif lines_diff[idx + 1] == "deleted file mode 100644":
                        summary += f"File deleted: **{file_name}**\n"
                    else:
                        summary += f"File modified: **{file_name}**\n"
            if (line.startswith('+') and not line.startswith('+++')) or (line.startswith('-') and not line.startswith('---')):
                content_file[os.path.join(os.getcwd(), *file_name.split("/"))] += line.strip()

        return summary, Seeds(
            iterable=[
                Seed(
                    asset=SeededAsset(
                        application=Settings.pieces_client.application,
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
                    ),
                    type="SEEDED_ASSET"
             for file_path, content in content_file.items()
            ]
        )
    except subprocess.CalledProcessError as e:
        show_error(f"Error fetching current working changes: {e}")
        return None

from rich.console import Console
from rich.markdown import Markdown
    if kwargs.get("all_flag", False):
        changes_summary, seeds = get_current_working_changes()
    commit_message = get_commit_message(changes_summary, seeds)
    if not commit_message:
            issue_number, issue_title, issue_markdown = get_issue_details(seeds)
        except TypeError:
    if r_message not in ["y", "c", ""]:
        print("Committing changes cancelled")
        return
    if r_message == "c":
        edit = input(f"Enter the new commit message [generated message is: '{commit_message}']: ")
        if edit:
            commit_message = edit

    if issue_flag:
        if issue_number:
            print("Issue Number: ", issue_number)
            print("Issue Title: ", issue_title)
            r_issue = input("Is this issue related to the commit? (y/n): ")
            if r_issue.lower() == "y":
                commit_message += f" (issue: #{issue_number})"
            else:
                issue_number = None
        if issue_number is None and issue_markdown:
            console = Console()
            md = Markdown(issue_markdown)
            console.print(md)
            validate_issue = True
            while validate_issue:
                issue_number = input("Issue number?\nLeave blank if none: ").strip()
                if issue_number.startswith("#") and issue_number[1:].isdigit():
                    issue_number = issue_number[1:]
                    validate_issue = False
                elif issue_number.isdigit():
                    validate_issue = False
                elif not issue_number:
                    break
            if not validate_issue:
                commit_message += f" (issue: #{issue_number})"

    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("Successfully committed with message:", commit_message)
        if kwargs.get('push', False):
            subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to commit changes:", e)


    from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
    from pieces_os_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions

            issue_number = Settings.pieces_client.qgpt_api.relevance(
                        application=Settings.pieces_client.application.id,
                        model=Settings.pieces_client.model_name,
            issue_markdown = ""
    from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
    from pieces_os_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions

        commit_message = Settings.pieces_client.qgpt_api.relevance(
                application=Settings.pieces_client.application.id,
                model=Settings.get_model_id(),
        show_error("Error in getting the commit message",e)