import requests
from bs4 import BeautifulSoup
import tkinter as tk


class Website:  # a class for getting data from the website
    def __init__(self, main_url):
        self.main_url = main_url
        self.announcements = []  # a list for storing the data from the Medipol website

    def get_page(self, page_number):  # a method for reaching pages
        page_url = f"{self.main_url}{page_number}"
        response = requests.get(page_url)
        if response.status_code == 200:  # that if condition checks if the connection between server of website and our program is successful or not
            return response.content
        else:
            print(f"Error: Failed to get data from page {int(page_url) +1}")
            return None

    def get_data(self):
        page_numbers = ['0', '1', '2', '3', '4']  # just takes first 5 pages
        for page_number in page_numbers:
            content = self.get_page(page_number)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                announcements = soup.find_all('div', class_='col-md-4 col-sm-6 list-card')  # find all cards
                for announcement in announcements:
                    title = announcement.find('a').text.strip()  # find and strip all 'a' tags
                    date = announcement.find('span',
                                             class_='date').text.strip()  # find and strip all 'span' tags with class 'date'
                    link_tag = announcement.find('a')  # find all 'a' tags
                    link = link_tag['href'] if link_tag else None # related tag is a href
                    full_link = link if link else None
                    self.announcements.append({
                        'title': title,
                        'date': date,
                        'link': full_link
                    })  # append all three of them to annoucements list
                print(f"{len(announcements)} announcements obtained from page {int(page_number)+ 1}.")


class GUI:  # a class for the program's GUI
    def __init__(self, root, announcements):
        self.root = root
        self.root.title("Announcements")  # temporary title, it will be changed
        self.announcements = announcements
        self.create_widgets()

    def get_title_from_div(self, soup):  # gets title from Medipol website and adds it to the title
        title_from_div = soup.find('div', id='block-medipol-page-title')  # find the title div
        if not title_from_div:
            return "Announcements"
        complete_title = "Medipol University Announcements: " + title_from_div.text.strip()
        return complete_title

    def create_widgets(self):
        # label for listboxes
        tk.Label(self.root, text="Announcements").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        tk.Label(self.root, text="URLs in the article").grid(row=0, column=2, sticky='w')
        # listbox for containing medipol annoucement website links
        self.listbox_for_link = tk.Listbox(self.root, width=100, height=20)
        self.listbox_for_link.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.listbox_for_link.bind('<<ListboxSelect>>', self.make_selection)
        # scrollbar for listbox_for_link
        scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.listbox_for_link.xview)
        scrollbar.grid(row=2, column=0, sticky='ew')
        self.listbox_for_link.config(xscrollcommand=scrollbar.set)

        # a listbox for urls in the contents
        self.listbox_for_urls = tk.Listbox(self.root, width=100, height=20)
        self.listbox_for_urls.grid(row=1, column=2, padx=10, pady=10, sticky='w')
        # a scrollbar for listbox_for_urls
        scrollbar_for_urls = tk.Scrollbar(self.root, orient="horizontal", command=self.listbox_for_urls.xview)
        scrollbar_for_urls.grid(row=2, column=2, sticky='ew')
        self.listbox_for_urls.config(xscrollcommand=scrollbar_for_urls.set)

        tk.Label(self.root, text="Content of Announcement", font=('Arial', 14)).grid(row=3, column=0, padx=10, pady=10,
                                                                                     sticky='w')
        self.title_label = tk.Label(self.root, text="", font=('Arial', 14))
        self.title_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        # a listbox to contain content of annoucements
        self.content_listbox = tk.Listbox(self.root, width=100, height=10)
        self.content_listbox.grid(row=5, column=0, padx=10, pady=10, sticky='w')
        # a scrollbar for content_listbox
        scrollbar2 = tk.Scrollbar(self.root, orient="horizontal", command=self.content_listbox.xview)
        scrollbar2.grid(row=6, column=0, sticky='ew')
        self.content_listbox.config(xscrollcommand=scrollbar2.set)

        # calls insert_to_listbox
        self.insert_to_listbox()

    def insert_to_listbox(self): # a function just to insert links to annoucements listbox
        for announcement in self.announcements:
            self.listbox_for_link.insert(tk.END, announcement['link'])

    def make_selection(self, event): # determines dates and links for selected annoucement
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            selected_announcement = self.announcements[index]
            selected_date = selected_announcement['date']
            selected_link = selected_announcement['link']

            self.title_label.config(text=f"Date: {selected_date}")
            self.get_content(selected_link)
            self.show_urls(selected_link)

    def get_content(self, link):
        response = requests.get(link)
        if response.status_code == 200: # checks connection
            soup = BeautifulSoup(response.content, 'html.parser')
            title = self.get_title_from_div(soup)
            self.root.title(title)
            # I observed that in every page id of paragraph paragraph--type--prg-text prg_id--{} paragraph--view-mode--default increases
            # so I adjusted get_content in order to check id's from range between 30330 to 31478 in order to not miss the contents
            main_class = 'paragraph paragraph--type--prg-text prg_id--{} paragraph--view-mode--default'
            content_ids = range(30330, 31498)
            content = ""
            for content_id in content_ids:
                content_div_class = main_class.format(content_id)
                content_div = soup.find('div', class_=content_div_class)
                if content_div:
                    content += content_div.get_text(strip=True) + "\n"

            if content.strip():
                self.content_listbox.delete(0, tk.END)
                self.content_listbox.insert(tk.END, content)
            else:
                self.content_listbox.delete(0, tk.END)
                self.content_listbox.insert(tk.END, "Content couldn't be found.")
        else:
            self.content_listbox.delete(0, tk.END)
            self.content_listbox.insert(tk.END, "Content couldn't be found.")

    def get_urls(self, soup): # get tag from a href in p in a
        urls = [a_tag['href'] for p_tag in soup.find_all('p') for a_tag in p_tag.find_all('a', href=True)]
        return urls

    def show_urls(self, link): # show urls that are from contents
        response = requests.get(link)
        if response.status_code == 200: # checks content
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = self.get_urls(soup)
            self.listbox_for_urls.delete(0, tk.END)
            for url in urls:
                if url != '/en/privacy':  # exclude unwanted URL
                    self.listbox_for_urls.insert(tk.END, url)
        else:
            self.listbox_for_urls.delete(0, tk.END)
            self.listbox_for_urls.insert(tk.END, "Url's couldn't be found.")


if __name__ == "__main__":
    main_url = "https://www.medipol.edu.tr/en/announcements?page="
    ws = Website(main_url)
    ws.get_data()
    announcements = ws.announcements

    root = tk.Tk()
    gui = GUI(root, announcements)
    root.mainloop()
