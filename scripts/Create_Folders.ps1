# Import the CSV file containing folder names and URLs.
# This is hard-coded for now, but at some point I'd like to scrape this content
# directly from https://projecteuler.net/.
$csv = Import-Csv -Path "Folder_Names.csv"

# Loop through each row in the CSV.
foreach ($row in $csv) {
    # Get the folder name from the 'folder' column.
    $folderName = $row.folder

    # Create a new directory with the specified name in the 'src' folder.
    New-Item -ItemType Directory -Path "..\src\$folderName"

    # Get the challenge title and url from the respective columns of the CSV.
    $title = $row.title
    $url = $row.url

    # Create a README.md file in the directory using the challenge title and URL.
    $readmeContent = "# $title`n`nTo get started please see the [challenge page]($url)"
    Set-Content -Path "..\src\$folderName\README.md" -Value $readmeContent
}