import tkinter as tk

#Def callback
def button_call():
    print("Debug button click")

root = tk.Tk()
root.geometry('500x400')
root.title('Villa Astrid Control Room')

sensors = {
    'LA1':    {'Sensor': 'Lilla Astrid  ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'LA2':    {'Sensor': 'Studio        ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'VA1':    {'Sensor': 'MH1           ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'VA2':    {'Sensor': 'MH2           ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'VA3':    {'Sensor': 'Parvi         ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'LH':     {'Sensor': 'Lilla Astrid  ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'OD1':    {'Sensor': 'Outdoor       ', 'Temp':0.0, 'Hum':0.0, 'Updated':''},
    'Water':  {'Sensor': 'Vesi -1m      ', 'Temp':0.0, 'Hum':0.0, 'Updated':''}
}

#Write text
text = tk.Label(root, text= sensors['LA1']['Sensor'])
text.pack()

label1 = tk.Label(root, text='Tkinter',bg='red',fg='white')
label2 = tk.Label(root,text='Pack Layout',bg='green', fg='white')
label3 = tk.Label(root, text='Demo',bg='blue', fg='white')

label1.pack()
label2.pack()
label3.pack()


#Create button
button = tk.Button(root, text= "Click here", bd = '5', command= button_call)
button.pack(side = 'top')



root.mainloop()