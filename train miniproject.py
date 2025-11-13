import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt


class TrainDataset:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def get_train_data(self, train_number):
        train_df = self.df[self.df["Train_Number"].astype(str) == str(train_number)]
        if train_df.empty:
            raise ValueError(f"Train number {train_number} not found in dataset!")
        return train_df

    def get_trains_between(self, from_station, to_station):
        subset = self.df[
            (self.df["Current_Station"].str.strip().str.lower() == from_station.strip().lower())
            & (self.df["Next_Station"].str.strip().str.lower() == to_station.strip().lower())
        ]
        return subset


class Train:
    def __init__(self, train_number, dataset):
        self.df = dataset.get_train_data(train_number)
        self.number = self.df["Train_Number"].iloc[0]
        self.name = self.df["Train_Name"].iloc[0]
        self.current_station = self.df["Current_Station"].iloc[0]
        self.next_station = self.df["Next_Station"].iloc[0]
        self.distance = self.df["Distance_Between_Stations_km"].iloc[0]
        self.time_to_next = self.df["Time_To_Reach_Next_min"].iloc[0]
        self.delay = self.df["Delay_Minutes"].iloc[0]
        self.expected_arrival = self.df["Expected_Arrival_CSMT"].iloc[0]
        self.status = self.df["Status"].iloc[0]
        self.last_updated = self.df["Last_Updated"].iloc[0]
        self.crowd_level = self.df["Crowd_Level"].iloc[0]
        self.train_type = self.df["Train_Type"].iloc[0]

    def get_summary(self):
        return (
            f" Train Number: {self.number}\n"
            f" Train Name: {self.name}\n"
            f" Current Station: {self.current_station}\n"
            f" Next Station: {self.next_station}\n"
            f" Distance to Next: {self.distance} km\n"
            f" Time to Reach Next: {self.time_to_next} min\n"
            f" Delay: {self.delay} min\n"
            f" Expected Arrival (CSMT): {self.expected_arrival}\n"
            f" Status: {self.status}\n"
            f" Crowd Level: {self.crowd_level}\n"
            f" Train Type: {self.train_type}\n"
            f" Last Updated: {self.last_updated}"
        )


class TrainTrackerUI:
    def __init__(self, root, dataset):
        self.root = root
        self.dataset = dataset
        self.root.title("🚄 Train Tracking System")
        self.root.geometry("800x650")
        self.root.configure(bg="#0a192f")

        title = tk.Label(
            root,
            text="Live Train Tracker",
            font=("Segoe UI Semibold", 24, "bold"),
            fg="#64ffda",
            bg="#0a192f",
        )
        title.pack(pady=20)

        frame = tk.Frame(root, bg="#112240", bd=2, relief="groove")
        frame.pack(pady=10, ipadx=10, ipady=10)

        
        tk.Label(
            frame,
            text="Enter Train Number:",
            font=("Segoe UI", 12),
            bg="#112240",
            fg="#ffffff",
        ).grid(row=0, column=0, padx=10, pady=5)

        self.train_entry = ttk.Entry(frame, width=25, font=("Segoe UI", 11))
        self.train_entry.grid(row=0, column=1, padx=10, pady=5)

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)

        ttk.Button(frame, text="🔍 Track Train", command=self.start_tracking).grid(
            row=0, column=2, padx=10, pady=5
        )

        
        stations = sorted(
            list(
                set(
                    self.dataset.df["Current_Station"].dropna().tolist()
                    + self.dataset.df["Next_Station"].dropna().tolist()
                )
            )
        )

        tk.Label(frame, text="From:", font=("Segoe UI", 12), bg="#112240", fg="#ffffff").grid(
            row=1, column=0, padx=10, pady=5
        )
        self.from_combo = ttk.Combobox(frame, values=stations, width=22, font=("Segoe UI", 11))
        self.from_combo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame, text="To:", font=("Segoe UI", 12), bg="#112240", fg="#ffffff").grid(
            row=1, column=2, padx=10, pady=5
        )
        self.to_combo = ttk.Combobox(frame, values=stations, width=22, font=("Segoe UI", 11))
        self.to_combo.grid(row=1, column=3, padx=10, pady=5)

        ttk.Button(
            frame, text="🚆 Search Trains Between", command=self.search_trains_between
        ).grid(row=2, column=1, columnspan=2, pady=10)

        ttk.Button(
            frame, text="📊 Show Route Delay", command=self.show_route_delay_chart
        ).grid(row=3, column=1, columnspan=2, pady=10)

        self.output_box = tk.Text(
            root,
            height=15,
            width=90,
            bg="#0a192f",
            fg="#d1d5db",
            font=("Consolas", 11),
            relief="solid",
            borderwidth=1,
            wrap="word",
        )
        self.output_box.pack(pady=20)

        tk.Label(
            root,
            text="Developed in Python + Tkinter + Matplotlib",
            font=("Segoe UI", 9),
            bg="#0a192f",
            fg="#8892b0",
        ).pack(side="bottom", pady=10)

    def start_tracking(self):
        train_number = self.train_entry.get().strip()
        if not train_number:
            messagebox.showwarning("Input Error", "Please enter a Train Number!")
            return

        try:
            train = Train(train_number, self.dataset)
            self.output_box.delete(1.0, tk.END)
            self.output_box.insert(tk.END, train.get_summary())
        except ValueError as e:
            messagebox.showerror("Train Not Found", str(e))

    def search_trains_between(self):
        from_station = self.from_combo.get()
        to_station = self.to_combo.get()

        if not from_station or not to_station:
            messagebox.showwarning("Input Error", "Please select both From and To stations!")
            return

        subset = self.dataset.get_trains_between(from_station, to_station)
        self.output_box.delete(1.0, tk.END)

        if subset.empty:
            self.output_box.insert(tk.END, f"No trains found between {from_station} and {to_station}.")
            return

        for _, row in subset.iterrows():
            self.output_box.insert(
                tk.END,
                f"🚆 {row['Train_Name']} ({row['Train_Number']})\n"
                f"Type: {row['Train_Type']} | Crowd: {row['Crowd_Level']} | Delay: {row['Delay_Minutes']} min\n"
                f"From: {row['Current_Station']} ➜ To: {row['Next_Station']}\n"
                f"Status: {row['Status']} | Updated: {row['Last_Updated']}\n\n"
            )

    def show_route_delay_chart(self):
        from_station = self.from_combo.get()
        to_station = self.to_combo.get()
        if not from_station or not to_station:
            messagebox.showwarning("Input Missing", "Please select both stations!")
            return

        subset = self.dataset.get_trains_between(from_station, to_station)
        if subset.empty:
            messagebox.showinfo("No Data", f"No trains found from {from_station} to {to_station}.")
            return

        plt.figure(figsize=(7, 4))
        plt.bar(subset["Train_Name"], subset["Delay_Minutes"], color="#64ffda")
        plt.title(f"Delay per Train: {from_station} to {to_station}")
        plt.xlabel("Train Name")
        plt.ylabel("Delay (Minutes)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    csv_path = "C:/Users/LAKSHITA/OneDrive/Desktop/clg/oops tut/train_miniproject/local_train_live_status_extended_updated.csv"
    dataset = TrainDataset(csv_path)

    root = tk.Tk()
    app = TrainTrackerUI(root, dataset)
    root.mainloop()
