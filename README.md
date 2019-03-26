# Inkscape Multipage Export
Inkscape extension to export selected objects to various file formats.

![Screenshot](https://raw.githubusercontent.com/olibia/inkscape-multipage-export/master/screenshot.png)

## Install
Copy extension files `multipage_export.inx` and `multipage_export.py` into `~/.config/inkscape/extensions`.
Inkscape needs to be restarted for the extension to appear.
`python2-lxml` and  `librsvg` must be installed for this extension to work.

### Inkscape Extensions
Download from Inkscape's Extensions page [here](https://inkscape.org/en/~olibia/%E2%98%85multipage-export-extension).

### Arch Linux
[AUR package](https://aur.archlinux.org/packages/inkscape-multipage-export)

## Usage
* Select the objects you want to export and from the Extensions menu choose Export and Multipage.
* Provide a name for the destination folder and select the export format.

Available formats are `PDF`, `PNG` and `SVG`.  
Available exporters are `rsvg`, and `inkscape`.  

*You can also name the exported files after the objects' IDs*  
*Combine PDFs requires `pdftk` installed in your system*

### Notes
Exported files are located at `~/Documents/Exports`.  
Tested only on Inkscape for Linux.

## License
[GPLv3](http://www.gnu.org/licenses/gpl-3.0.en.html)
