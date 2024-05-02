# Scripts

In a vague attempt to keep my sanity intact, I wrote some (quick and dirty) scripts in this folder to automatically generate the folder structure, based on the details within [Folder_Names.csv](./Folder_Names.csv). It would be nice to scrape the details directly from [Project Euler](https://projecteuler.net/), but it didn't seem worth it for just 100 challenges.

My nasty method involved copy-pasting the titles from [the archives section](https://projecteuler.net/archives) into a .csv file to use as the "title", sanitising the name with underscores etc. to use as the "folder", and generating the link *automagically*. This is trivial since someone at Project Euler was nice enough use easy-to-generate links like `https://projecteuler.net/problem=1`.

Then, I wrote a quick [PowerShell script](./Create_Folders.ps1) to create the folders inside [src](../src/) and initialise a README.md (so the folders can be committed with `git`).

## Adding More Challenges

To add more challenges, simply add more rows with the relevant data into [File_Names.csv](./Create_Folders.ps1), and then run [Create_Folders.ps1](./Create_Folders.ps1) from within the `scripts` folder (It relies on relative paths from `scripts/`... sorry!).

Alternatively, if you're annoyed enough by this approach, feel free to make an automagic tool that can scrape the [Project Euler archives](https://projecteuler.net/archives) to create the folders without manual intervention. I certainly won't complain if you PR this in either...