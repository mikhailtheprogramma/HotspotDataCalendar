import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, FileLink
import os

# File upload widget
file_upload = widgets.FileUpload(
    accept='.csv',  # Accept only CSV files
    multiple=False  # Allow only a single file upload
)
upload_button = widgets.Button(description="Process File")
download_button = widgets.Button(description="Download Image")
output = widgets.Output()

# Configuration panel widgets for column selection
timestamp_column_dropdown = widgets.Dropdown(description="Timestamp Column", options=[])

# Display configuration panel and widgets
display(widgets.VBox([file_upload, upload_button, timestamp_column_dropdown, download_button, output]))

# Placeholder for the file name of the saved plot
saved_plot_path = "calendar_heatmap.png"

def process_file(change):
    global saved_plot_path
    with output:
        output.clear_output()  # Clear previous output
        if not file_upload.value:
            print("Please upload a file first.")
            return
        
        file_content = file_upload.value[0]['content']
        
        # Create a temporary file to read the CSV
        with open('temp.csv', 'wb') as f:
            f.write(file_content)

        # Read the CSV file into a DataFrame
        data = pd.read_csv('temp.csv')

        # Remove the temporary file
        os.remove('temp.csv')

        print("File uploaded and processed successfully!")

        # Update dropdown options based on columns in the CSV
        timestamp_column_dropdown.options = data.columns.tolist()

        # Ensure the user selects the correct timestamp column
        if not timestamp_column_dropdown.value:
            print("Please select the Timestamp column.")
            return

        # Extract the selected Timestamp column
        Timestamps = data[timestamp_column_dropdown.value]

        # Create a 1D array to hold Event counts for each day (1-31)
        Event_counts = np.zeros(31)  # 31 days
        
        # Count Events for each day
        for timestamp in Timestamps:
            Date = timestamp.split(' ')[0]
            try:
                Day = int(Date.split('-')[-1])  # Extract day of the month
                if 1 <= Day <= 31:  # Validate that Day is between 1 and 31
                    Event_counts[Day-1] += 1  # Increment the Event count for that day
                else:
                    print(f"Invalid day detected: {Day}. Skipping.")
            except ValueError:
                print(f"Invalid timestamp format: {timestamp}. Skipping.")

        # Normalize the Event counts to a ratio (0-1)
        max_count = np.max(Event_counts)
        normalized_counts = Event_counts / max_count if max_count > 0 else Event_counts

        # Set up the plot (calendar-like heatmap)
        fig, ax = plt.subplots(figsize=(10, 10))

        # Calendar layout: 7 columns (days of the week) and 5 rows (max days in a month)
        ax.set_xticks(np.arange(7))  # 7 days of the week
        ax.set_xticklabels(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], rotation=0)
        
        # Fill the days of the month into a 5x7 grid
        ax.set_yticks(np.arange(5))  # Up to 5 rows for 31 days
        ax.set_yticklabels([])  # No y-tick labels
        
        # Arrange days in the grid starting from the correct weekday (1st of the month)
        # Assume the 1st day of the month is Sunday (change this as needed)
        first_day_of_month = 0  # Sunday (0), Monday (1), ..., Saturday (6)
        
        # Create a matrix for the calendar, filling in the days of the month
        calendar_matrix = np.full((5, 7), fill_value=np.nan)  # 5 rows and 7 columns
        for day in range(1, 32):  # Loop through all days of the month (1 to 31)
            row = (first_day_of_month + day - 1) // 7
            col = (first_day_of_month + day - 1) % 7
            calendar_matrix[row, col] = day

        # Plot each day in the calendar
        for row in range(5):
            for col in range(7):
                day = calendar_matrix[row, col]
                if not np.isnan(day):
                    # Determine the color for each day based on the normalized Event count
                    color = plt.cm.YlOrRd(normalized_counts[int(day)-1])
                    ax.add_patch(plt.Rectangle((col, row), 1, 1, color=color))
                    # Add the day number in the center of the cell
                    ax.text(col + 0.5, row + 0.5, f"{int(day)}", ha='center', va='center', fontsize=12, color='black')

        # Set limits and aspect for the calendar grid
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')

        # Add a colorbar for the heatmap
        cbar = fig.colorbar(plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=0, vmax=1)), ax=ax)
        cbar.set_label('Event Density (0 to 1)', rotation=270, labelpad=20)

        # Save the plot to a file
        fig.tight_layout()
        fig.savefig(saved_plot_path, bbox_inches='tight')
        plt.close(fig)  # Close the figure to avoid display issues
        print(f"Calendar heatmap saved as {saved_plot_path}")

def download_plot(change):
    with output:
        if not os.path.exists(saved_plot_path):
            print("No plot to download. Please generate the plot first.")
            return
        
        # Provide a download link
        display(FileLink(saved_plot_path, result_html_prefix="Click here to download the calendar heatmap: "))

# Attach event handlers to the buttons
upload_button.on_click(process_file)
download_button.on_click(download_plot)
