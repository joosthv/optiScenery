import os
import sys  # Import sys to get the executable path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import configparser

# Define the current_dir variable by getting the directory where the script or the executable is located
current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

# Configuration file path
config_file = os.path.join(current_dir, 'settings.ini')

# Ensure the configuration directory exists
os.makedirs(os.path.dirname(config_file), exist_ok=True)

# Load the configuration file
config = configparser.ConfigParser()
config.read(config_file)

def save_config(directory):
    if not config.has_section('Settings'):
        config.add_section('Settings')
    config.set('Settings', 'CommunityFolder', directory)
    with open(config_file, 'w') as f:
        config.write(f)

def get_saved_directory():
    return config.get('Settings', 'CommunityFolder') if config.has_section('Settings') and config.has_option('Settings', 'CommunityFolder') else ''

def list_airport_directories(directory):
    results = []
    unexpected_format = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir() and 'airport-' in entry.name.lower():
                parts = entry.name.split('airport-')
                if len(parts) == 2:
                    # Assuming everything before 'airport-' is publisher
                    publisher = parts[0].rstrip('-')
                    # After 'airport-', the first part is the ICAO code, the rest is the airport name
                    airport_parts = parts[1].split('-')
                    ICAO_code = airport_parts[0].upper()  # ICAO code in uppercase
                    airport_name = '-'.join(airport_parts[1:])  # The rest is the airport name
                    results.append([publisher, ICAO_code, airport_name])
                else:
                    unexpected_format.append(entry.name)
    return results, unexpected_format

# New function to sort tree data
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    
    # Sort, placing "Unexpected Format" entries at the end always
    l.sort(key=lambda x: (x[0] == "Unexpected Format", x[0]), reverse=reverse)
    
    # Rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # Reverse sort next time
    tv.heading(col, command=lambda _col=col: treeview_sort_column(tv, _col, not reverse))


    
# GUI part
def populate_list():
    for i in tree.get_children():
        tree.delete(i)
    results, unexpected_format = list_airport_directories(directory_to_index)
    
    # Insert sorted results
    for row in results:
        tree.insert('', 'end', values=row)
    
    # Now insert unexpected format entries at the bottom with a special marker
    for name in unexpected_format:
        # Insert at the end and mark the Publisher as "Unexpected Format"
        tree.insert('', 'end', values=("Unexpected Format", '', name))


def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        global directory_to_index
        directory_to_index = directory
        save_config(directory)  # Save the selected directory
        populate_list()

def main_gui():
    global tree, directory_to_index
    root = tk.Tk()
    root.title("OptiFlight Scenery Finder 1.0")

    # Set the window icon
    icon_path = 'C:\Projects\icon.png'  # The icon.png should be in the current working directory or provide the full path
    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon)

    # Include logo
    logo_path = 'C:\Projects\logo.png'  # The logo.png should be in the current working directory or provide the full path
    if os.path.exists(logo_path):
        logo = tk.PhotoImage(file=logo_path)
        logo_label = tk.Label(root, image=logo)
        logo_label.image = logo  # Keep a reference!
        logo_label.pack()


    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=10, pady=10)

    select_button = tk.Button(frame, text="Select Community Folder", command=select_directory)
    select_button.pack(side=tk.RIGHT)

    # Treeview setup
    tree = ttk.Treeview(root, columns=('Publisher', 'ICAO Code', 'Airport Name'), show='headings')
    tree.heading('Publisher', text='Publisher', command=lambda: treeview_sort_column(tree, 'Publisher', False))
    tree.heading('ICAO Code', text='ICAO Code', command=lambda: treeview_sort_column(tree, 'ICAO Code', False))
    tree.heading('Airport Name', text='Airport Name', command=lambda: treeview_sort_column(tree, 'Airport Name', False))
    tree.pack(fill=tk.BOTH, expand=True)

    directory_to_index = get_saved_directory()  # Get the saved directory if available
    if directory_to_index:
        populate_list()  # Populate the list if a directory is already saved

    root.mainloop()

if __name__ == '__main__':
    directory_to_index = ''  # Start with no directory
    main_gui()
