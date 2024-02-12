from tkinter import *
from tkinter import ttk
from googletrans import LANGUAGES
from translate import Translator

def change(text="type",src_lan="English",dest_lan="HINDI"):
    text1=text
    srclan1=src_lan
    destlan1=dest_lan
    translator=Translator(to_lang=destlan1)
    translation= translator.translate(text1)
    return translation

def data():
    s=combo_src.get()
    d=combo_dest.get()
    msg=src_txt.get(1.0,END)
    textget= change(msg,s,d)
    dest_txt.delete(1.0,END)
    dest_txt.insert(END,textget)

root=Tk()
root.title("Translator")
root.geometry("500x800")
root.config(bg="black")
lab_txt=Label(root,text="Translator",font=("Times New Roman",40,"bold"))
lab_txt.place(x=100,y=40,height=50,width=300)

frame=Frame(root).pack(side=BOTTOM)

lab_src_txt=Label(root,text="Source Text",font=("Times New Roman",20,"bold"),fg='dark blue')
lab_src_txt.place(x=100,y=110,height=20,width=300)
src_txt=Text(frame,font=("Times New Roman",20,"bold"),wrap=WORD)
src_txt.place(x=10,y=140,height=100,width=480)

list_text=list(LANGUAGES.values())
combo_src=ttk.Combobox(frame,value=list_text)
combo_src.place(x=10,y=260,height=40,width=150)
combo_src.set("english")

button_change=Button(frame,text="Translate",relief=RAISED,command=data)
button_change.place(x=175,y=260,height=40,width=150)

combo_dest =ttk.Combobox(frame,value=list_text)
combo_dest.place(x=340,y=260,height=40,width=150)
combo_dest.set("english")

lab_src_txt=Label(root,text="Destination Text",font=("Times New Roman",20,"bold"),fg='dark blue')
lab_src_txt.place(x=100,y=320,height=20,width=300)
dest_txt=Text(frame,font=("Times New Roman",20,"bold"),wrap=WORD)
dest_txt.place(x=10,y=350,height=100,width=480)
root.mainloop()

