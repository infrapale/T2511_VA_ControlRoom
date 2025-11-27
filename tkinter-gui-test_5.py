import tkinter as tk
import time




class App(tk.Tk):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Tkinter Pack Layout')
        self.root.geometry('600x400')
        self.indx = 0
        self.txt = "Nbr= {0}".format(self.indx)
        print(self.txt)
        self.label1 = tk.Label(self.root, text='Pack',bg='red',fg='white')
        self.label2 = tk.Label(self.root, text='Pack',bg='green', fg='white')
        self.label3 = tk.Label(self.root, text=self.txt,bg='blue', fg='white')
        self.label4 = tk.Label(self.root, text='Pack',bg='purple', fg='white')

        self.label1.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.label2.pack(side=tk.TOP, fill=tk.X, pady=20)
        self.label3.pack(side=tk.TOP, fill=tk.X ,pady=40)
        self.label4.pack(side=tk.LEFT, pady=60)
        self.indx = self.indx+1
    
def main():
    app = App()
    app.mainloop()
    time.sleep(2.0)
    

main()

