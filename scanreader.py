'''ScanReaderPro, un projet réalisé par Viktor Brothier (et Emil Can) dans le cadre
du cours d'ISN de Mr Gaudon.'''
import os
import sys
#from tkinter import*
import tkinter as tk
from tkinter import filedialog,messagebox,colorchooser
import PIL
from PIL import Image, ImageTk
import zipfile
import datetime
import webbrowser
import ctypes

'''WIP zoom, log, (couleurs)'''

class Mainwindow: #par Viktor :)
    def __init__(self):
        #Set--------
        self.root=tk.Tk()
        self.root.geometry('600x700')
        ctypes.windll.shcore.SetProcessDpiAwareness(1) #ouiiiii
        self.root.minsize(425,81)
        self.root.title('ScanReaderPro')
        #Colors-----
        self.headerColor='#931621'
        self.headerActiveColor='#7a111a'
        self.bodyColor='#f5e0b7'
        self.bodyActiveColor='#d6be90'
        self.root['bg']=self.bodyColor
        #winblue 0078d7 3393DF
        #red     931621 7a111a
        #grey    28464b 326771
        #bigblue 2c8c99 1f646e
        #green   229c5c 29c272
        #body    f5e0b7 d6be90
        #Shortcuts--
        self.root.bind('<Control-n>',self.openManga)
        self.root.bind('<Button-3>',self.rightclick)
        #Images-----
        self.logo=tk.PhotoImage(file=str(os.getcwd())+"/icons/logo.png")
        self.addicon=tk.PhotoImage(file=str(os.getcwd())+"/icons/add.png")
        self.menuicon=tk.PhotoImage(file=str(os.getcwd())+"/icons/menu.png")
        self.glassicon=tk.PhotoImage(file=str(os.getcwd())+"/icons/glass.png")
        #Header-----
        self.header=tk.Frame(self.root,width=1,height=self.logo.height()+20,bg=self.headerColor)
        self.header.pack(side='top', anchor='nw', fill='x')
        #logo
        self.logoCanvas=tk.Canvas(self.header,width=self.logo.width()+20,
                               height=self.logo.height()+20,bg=self.headerColor,
                               highlightthickness=0)
        self.logoCanvas.pack(side='left')
        self.logoCanvas.create_image((self.logo.width()+20)/2,(self.logo.height()+20)/2,
                                     anchor='center',image=self.logo)
        self.emptyspace1=tk.Frame(self.header,width=30,height=1,bg=self.headerColor)
        self.emptyspace1.pack(side='right')
        #settings menu
        self.settingsButton=tk.Menubutton(self.header,image=self.menuicon,width=32,height=32,
                                     bg=self.headerColor,bd=0,cursor='hand2',
                                     activebackground=self.headerActiveColor)
        self.settingsButton.pack(side='right')
        self.settings=tk.Menu(self.settingsButton,tearoff=0)
        self.settings.add_command(label='Clear library')
        self.readdir=tk.Menu(self.settings,tearoff=0)
        self.orientation=False
        self.readdir.add_command(label='Manga',command=self.orientation_m)
        self.readdir.add_command(label='Comics',command=self.orientation_c)
        self.settings.add_cascade(label='Reading direction', menu=self.readdir)
        self.settings.add_command(label='Help',command=self.readme)
        #self.settings.add_command(label='group by series')
        #self.sortby=tk.Menu(self.settings,tearoff=0)
        #self.sortby.add_command(label='Sort A-Z')
        #self.sortby.add_command(label='Sort by time')
        #self.settings.add_cascade(label='Sort by', menu=self.sortby)
        #self.displayas=tk.Menu(self.settings,tearoff=0)
        #self.displayas.add_command(label='Images')
        #self.displayas.add_command(label='List')
        #self.settings.add_cascade(label='Display as', menu=self.displayas)
        self.settingsButton['menu']=self.settings
        self.emptyspace2=tk.Frame(self.header,width=18,height=1,bg=self.headerColor)
        self.emptyspace2.pack(side='right')
        #add button
        self.addButton=tk.Button(self.header,image=self.addicon,width=30,height=30,
                              bg=self.headerColor,bd=2,relief='flat',cursor='hand2',
                              command=self.openManga)
        self.addButton.pack(side='right')
        self.addButton.bind('<Enter>',self.addButton_enter)
        self.addButton.bind('<Leave>',self.addButton_leave)
        self.emptyspace3=tk.Frame(self.header,width=40,height=1,bg=self.headerColor)
        self.emptyspace3.pack(side='right')
        self.manga=None
        #search bar
        self.searchbar=tk.Frame(self.header,width=152,height=27,bg=self.headerColor)
        self.searchbar.pack(side='right')
        self.searchCanvas=tk.Canvas(self.searchbar,width=152,height=27,bg=self.headerColor,
                                 highlightthickness=0)
        self.searchCanvas.place(anchor='nw')
        self.searchCanvas.create_oval(0,0,25,25,fill=self.bodyColor,width=0)
        self.searchCanvas.create_oval(125,0,150,25,fill=self.bodyColor,width=0)
        self.searchCanvas.create_rectangle(12.5,0,137.5,25+1,fill=self.bodyColor,width=0)
        self.searchCanvas.create_image(15,13,image=self.glassicon)
        self.searchbar=tk.Entry(self.searchbar,width=18,bg=self.bodyColor,bd=0,fg='grey')
        self.searchbar.place(x=28,y=5)
        self.searchbar.insert(tk.END,'Search')
        self.searchbar.bind('<Button-1>',self.searchclicked)
        self.searchbar.bind('<Return>',self.search)
        #Body-------
        self.colnames=tk.Frame(self.root,width=1,height=50,bg=self.bodyColor)
        self.colnames.pack(side='top', anchor='nw', fill='x',padx=10,pady=10)
        self.libraryline=tk.Canvas(self.root,width=580,height=1,bg=self.bodyColor,
                                highlightthickness=0)
        self.libraryline.create_line(0,0,580,0,width=1)
        self.libraryline.pack(side='top',fill='x',padx=10)
        self.body=tk.Frame(self.root,width=1,height=1,bg=self.bodyColor)
        self.body.pack(side='left', anchor='nw',expand='yes', fill='both',padx=10,pady=10)
        self.liblistbox_name=tk.Listbox(self.body,bg=self.bodyColor,bd=0,cursor='hand2',
                                selectbackground=self.bodyActiveColor,selectmode=tk.SINGLE,highlightthickness=0)
        self.liblistbox_name.pack(side='left',fill='both',expand='yes')
        self.liblistbox_prog=tk.Listbox(self.body,width=15,bg=self.bodyColor,bd=0,
                                selectbackground=self.bodyColor,selectmode=tk.SINGLE,highlightthickness=0)
        self.liblistbox_prog.pack(side='left',fill='y',expand='no')
        self.liblistbox_date=tk.Listbox(self.body,width=15,bg=self.bodyColor,bd=0,
                                selectbackground=self.bodyColor,selectmode=tk.SINGLE,highlightthickness=0)
        self.liblistbox_date.pack(side='left',fill='y',expand='no')
        self.liblistbox_path=tk.Listbox(self.body,bg=self.bodyColor,bd=0,
                                selectbackground=self.bodyColor,selectmode=tk.SINGLE,highlightthickness=0)
        self.liblistbox_path.pack(side='left',fill='both',expand='yes')
        self.openlibcounter=0
        self.liblistbox_name.bind('<Double-1>',self.preOpenLib)
        self.scrollbar=tk.Scrollbar(self.body,bg='#28464b',activebackground='#326771',command=self.scrollin)
        self.scrollbar.pack(side='right',fill='y')
        self.liblistbox_name['yscrollcommand']=self.scrollbar.set
        self.liblistbox_prog['yscrollcommand']=self.scrollbar.set
        self.liblistbox_date['yscrollcommand']=self.scrollbar.set
        self.liblistbox_path['yscrollcommand']=self.scrollbar.set
        #library
        self.colnames.bind('<Configure>',self.resizegrid)
        self.library=[]
        self.librarywid=[]
        self.libraryLabel_name=tk.Label(self.colnames,text='Name',bg=self.bodyColor,justify='left')
        self.libraryLabel_name.pack(side='left',fill='x',expand='yes',anchor='w')
        self.libraryLabel_prog=tk.Label(self.colnames,text='Progression',bg=self.bodyColor,
                                     justify='left')
        self.libraryLabel_prog.pack(side='left',fill='x',anchor='w')
        self.libraryLabel_date=tk.Label(self.colnames,width=12,text='Import Date',bg=self.bodyColor,
                                     justify='left')
        self.libraryLabel_date.pack(side='left',fill='x',anchor='w')
        self.libraryLabel_path=tk.Label(self.colnames,text='Path',bg=self.bodyColor,justify='left')
        self.libraryLabel_path.pack(side='left',fill='x',expand='yes',anchor='w')
        self.searchlistboxes=()
        
        self.root.mainloop()

    def scrollin(self,*args):
        self.liblistbox_name.yview(*args)
        self.liblistbox_prog.yview(*args)
        self.liblistbox_date.yview(*args)
        self.liblistbox_path.yview(*args)
    def openManga(self,evt=None): #main function to open a manga file when add clicked
        if self.manga:
            self.errorMessage('Close the opened manga first')
            return None
        self.manga_zip=filedialog.askopenfilename(initialdir='F:/Comics',
                                                  title='Select Manga File',
                                                  filetypes=(("zip files","*.zip"),
                                                             ("all files","*.*")))
        try:
            self.manga=zipfile.ZipFile(self.manga_zip)
            self.manga_name_o=''.join(list(os.path.basename(self.manga.filename))[:-4])
            self.manga_path=self.manga.filename
            if self.manga.testzip()==None:
                self.openMangaCall()
            else:
                self.errorMessage('Corrupted zip file')
                return None
        except zipfile.BadZipFile:
            self.errorMessage('Bad zip file')
        except zipfile.LargeZipFile:
            self.errorMessage('File is too large')
        except FileNotFoundError: pass
    def openMangaCall(self): #second part of openManga
        self.dirlist=[]
        self.imglist=[]
        self.manga_date=datetime.date.today()
        self.manga_dateplus=datetime.datetime.now()
        for i in self.manga.namelist():
            self.file_info=self.manga.getinfo(i)
            if self.file_info.is_dir():
                self.dirlist.append(self.file_info.filename)
            if (self.file_info.filename.endswith('.jpg') or
                self.file_info.filename.endswith('.png') or
                self.file_info.filename.endswith('.jpeg')):
                self.imglist.append(self.file_info.filename)
        self.imglistlist=[]
        if len(self.dirlist)==0:
            self.manga_name=self.manga_name_o
            self.manga_info=[self.manga_name,'',self.manga_date,self.manga_path]
            if len(self.imglist)==0:
                self.errorMessage('No valid images')
                self.manga.close()
                self.manga=None
                return None
            TL(self) #1
        elif len(self.dirlist)>0:
            for i,diri in enumerate(self.dirlist):
                self.imglistlist.append([])
                for n in self.imglist:
                    if n.startswith(diri):
                        self.imglistlist[i].append(n)
            if len(self.dirlist)==1:
                self.manga_name=self.manga_name_o
                self.manga_info=[self.manga_name,'',self.manga_date,self.manga_path]
                TL(self,0) #2
            elif len(self.dirlist)>1:
                for i,diri in enumerate(self.dirlist):
                    self.manga_name=self.manga_name_o+' - '+diri
                    self.manga_info=[self.manga_name,'',self.manga_date,self.manga_path]
                    self.indice=i
                    TL(self,i) #3
    def addButton_enter(self,evt): #hovering of add button
        self.addButton['bg']=self.headerActiveColor
    def addButton_leave(self,evt): #hovering of add button
        self.addButton['bg']=self.headerColor
    def errorMessage(self,errorType): #the standard error message
        messagebox.showwarning(title='ERROR',message=errorType,default='ok')
    def rightclick(self,evt): #displays a rightclick menu in root
        self.rightmenu=tk.Menu(self.root,tearoff=0)
        self.rightmenu.add_command(label='Copy path')
        self.rightmenu.add_command(label='Delete this Manga')
        self.rightmenu.add_command(label='Delete all Mangas')
        self.rightmenu.tk_popup(evt.x_root,evt.y_root)
    def readme(self): #help page
        webbrowser.open('file:///'+os.getcwd()+'/readme.htm',2)
    def orientation_m(self):
        self.orientation=True
    def orientation_c(self):
        self.orientation=False
    def searchclicked(self,evt):
        self.searchbar.delete(0,tk.END)
        self.searchbar['fg']='black'
    def resizegrid(self,evt):
        self.libraryline['width']=self.root.winfo_width()
        self.libraryline.delete('all')
        self.libraryline.create_line(0,0,self.root.winfo_width(),0,width=1)
    def libManager(self,tl):
        self.root.wait_window(tl.returnroot())
        if len(self.dirlist)>1:
            if self.indice+1==len(self.dirlist):
                self.manga.close()
                self.manga=None
            else: pass
        else:
            self.manga.close()
            self.manga=None
        current,total=tl.returncurrent()
        if current==total:
            self.manga_info[1]='Finished!'
        else:
            self.manga_info[1]='page '+str(current)+' /'+str(total)
        self.library.append(self.manga_info)
        if len(self.searchlistboxes)>0: #if in search switch to normal and vice verca
            for i in self.searchlistboxes:
                i.delete(0,tk.END)
        else: pass
        self.liblistbox_name.insert(0,self.manga_info[0])
        self.liblistbox_prog.insert(0,self.manga_info[1])
        self.liblistbox_date.insert(0,self.manga_info[2])
        self.liblistbox_path.insert(0,self.manga_info[3])
        self.liblistboxes=(self.liblistbox_name,self.liblistbox_prog,
                           self.liblistbox_date,self.liblistbox_path)
        self.duplicateDel(self.liblistboxes)
    def duplicateDel(self,displaytuple): #looking for duplicates
        pathlb=displaytuple[3]
        print(self.library)
        print(pathlb.get(0,tk.END))
        for i,obji in enumerate(list(pathlb.get(0,tk.END))): #looking for duplicates
            for j,objj in enumerate(list(pathlb.get(0,tk.END))):
                if i!=j and obji==objj:
                    print(i,j)
                    if i<j: 
                        try:
                            for n in displaytuple:
                                n.delete(j)
                            del(self.library[j])
                            return None
                        except: pass
                    elif i>j:
                        try:
                            for n in displaytuple:
                                n.delete(i)
                            del(self.library[i])
                            return None
                        except: pass
        return None
    def preOpenLib(self,evt): #avoid openlib to be called twice
        self.openlibcounter+=1
        if self.openlibcounter==2:
            self.openlibcounter=0
            self.openLib()
    def openLib(self):
        selindextup=self.liblistbox_name.curselection()
        if selindextup==():
            return None
        selindex=selindextup[0]
        currentpath=list(self.liblistbox_path.get(0,tk.END))[selindex]
        if self.manga:
            self.errorMessage('Close the opened manga first')
            return None
        try:
            self.manga=zipfile.ZipFile(currentpath,'r')
            self.manga_name_o=''.join(list(os.path.basename(self.manga.filename))[:-4])
            self.manga_path=currentpath
            if self.manga.testzip()==None:
                self.openMangaCall()
            else:
                self.errorMessage('Corrupted zip file')
                return None
        except zipfile.BadZipFile:
            self.errorMessage('Bad zip file')
        except zipfile.LargeZipFile:
            self.errorMessage('File is too large')
        except FileNotFoundError:
            self.errorMessage("File have been deleted or moved,\n try to find the file from the 'Add' buton")
    def search(self,evt): #function of the searchbar
        #double click on search result TO TEST
        value=self.searchbar.get()
        self.searchbar.delete(0,tk.END)
        self.searchbar['fg']='grey'
        self.searchbar.insert(tk.END,'Search')
        value=value.lower()
        l=list(value)
        try:
            for i in range(len(l)):
                l.remove(' ')
        except: pass
        value=''.join(l)
        print(value)
        libnamelist=[]
        namesearch=[]
        self.searchwid=[]
        #reversedlib=self.library[::-1]
        for i,libi in enumerate(self.library):
            a=libi[0].lower()
            h=list(a)
            try:
                for n in range(len(h)):
                    h.remove(' ')
                n=0 #pour pas avoir unused variable
            except: pass
            a=''.join(h)
            print(a)
            libnamelist.append([a,libi])
        for i in libnamelist:
            if i[0].startswith(value) or i[0].endswith(value):
                namesearch.append(i[1])
        if len(self.searchlistboxes)>0: #if in search switch to normal and vice verca
            for i in self.searchlistboxes:
                i.delete(0,tk.END)
        elif len(self.liblistboxes)>0: 
            for i in self.liblistboxes:
                i.delete(0,tk.END)
        else: pass
        print(namesearch)
        for i in namesearch:
            self.liblistbox_name.insert(0,i[0])
            self.liblistbox_prog.insert(0,i[1])
            self.liblistbox_date.insert(0,i[2])
            self.liblistbox_path.insert(0,i[3])
        self.searchlistboxes=(self.liblistbox_name,self.liblistbox_prog,
                              self.liblistbox_date,self.liblistbox_path)
        self.duplicateDel(self.searchlistboxes)

#-----------------------------------------------------------------------------------------------

class TL():   #par Viktor ;*
    def __init__(self,main,indice=None): #creates the toplevel where images are displayed
        self.root=tk.Toplevel(takefocus=1)
        self.root.geometry('600x700')
        self.root.focus_set()
        self.main=main
        if indice==None:
            self.imglist=main.imglist
        else:
            self.imglist=main.imglistlist[indice]
        if self.main.orientation:
            self.orifwd='<Left>'
            self.oriback='<Right>'
        else:
            self.orifwd='<Right>'
            self.oriback='<Left>'
        if len(self.imglist)==0:
            self.main.errorMessage('No valid images')
            self.quitwin()
            return None
        self.root.title(main.manga_name)
        self.root['bg']='black'
        self.totalpage=len(self.imglist)-1
        self.current=0
        self.header=tk.Frame(self.root,width=1,height=26,bg='black')
        self.header.pack(side='bottom',anchor='nw',fill='x')
        self.index=tk.Frame(self.header,width=100,height=26,bg='black')
        self.indexEntry=tk.Entry(self.index,width=4)
        self.indexEntry.pack(side='left')
        self.indexEntry.insert(tk.END,self.current)
        self.indexText=tk.Label(self.index,text='/ '+str(self.totalpage),
                             bg='black',fg='white')
        self.indexText.pack(side='left')
        self.zoominicon=tk.PhotoImage(file=str(os.getcwd())+"/icons/zoomin.png")
        self.zoomouticon=tk.PhotoImage(file=str(os.getcwd())+"/icons/zoomout.png")
        self.zoomin=tk.Button(self.header,image=self.zoominicon,width=23,height=23,
                              bg='black',bd=2,relief='flat',cursor='hand2',
                              command=self.zoomon)
        self.zoomout=tk.Button(self.header,image=self.zoomouticon,width=23,height=23,
                              bg='black',bd=2,relief='flat',cursor='hand2',
                              command=self.zoomoff)
        self.zoomout.pack(side='right')
        self.zoomin.pack(side='right')
        self.emptyspace1=tk.Frame(self.header,width=30,height=1,bg='black')
        self.emptyspace1.pack(side='right')
        self.index.pack(side='right')
        self.zoom=False
        self.pC=tk.Canvas(self.root,width=1,height=1,bg='black',highlightthickness=0)
        self.pC.pack(expand='yes', fill='both')
        self.tlh=self.root.winfo_height()-26
        self.tlw=self.root.winfo_width()
        self.pC.bind('<Configure>',self.change)
        self.root.bind('<Right>',self.turnfwd)
        self.root.bind('<Left>',self.turnback)
        self.pC.bind('<Button-1>',self.testclick)
        self.indexEntry.bind('<Return>',self.getentry)
        self.change()
        main.libManager(self)
    def change(self,evt=None): #creates images and resize it if user resize window
        self.pilerrorcounter=0
        try:
            self.p=Image.open(self.main.manga.open(self.imglist[self.current]))
            self.tlh=self.root.winfo_height()-26
            self.tlw=self.root.winfo_width()
            imgw=self.p.width
            imgh=self.p.height
            if imgw/imgh < self.tlw/self.tlh:
                newimgw=round((self.tlh*imgw)/imgh)
                newimgh=self.tlh
            else:
                newimgw=self.tlw
                newimgh=round((self.tlw*imgh)/imgw)
            self.p=self.p.resize((round(newimgw*1.015),round(newimgh*1.015)))
            self.pC.delete('all')
            ptk=ImageTk.PhotoImage(self.p)
            self.pC.create_image(self.tlw/2,self.tlh/2,anchor='center',image=ptk)
            self.pC.image=ptk
            return self.p
        except PIL.UnidentifiedImageError:
            self.pilerrorcounter+=1
            return None
    def zoomon(self):
        self.zoom=True
    def zoomoff(self):
        self.zoom=False
    def turnfwd(self,evt=None): #turn page forward
        if self.current!=self.totalpage:
            self.root.bind(self.orifwd,self.turnfwd)
        if self.current>0:
            self.root.bind(self.oriback,self.turnback)
        if self.current==self.totalpage:
            self.quitwin()
        else:
            self.current+=1
            self.p=self.change()
            self.indexEntry.delete(0,tk.END)
            self.indexEntry.insert(tk.END,self.current)
            return self.p
    def turnback(self,evt=None): #turn page back
        if self.current!=self.totalpage:
            self.root.bind(self.orifwd,self.turnfwd)
        if self.current>0:
            self.root.bind(self.oriback,self.turnback)
        if self.current==0:
            self.root.unbind(self.oriback)
        else:
            self.current-=1
            self.p=self.change()
            self.indexEntry.delete(0,tk.END)
            self.indexEntry.insert(tk.END,self.current)
            return self.p
    def testclick(self,evt):
        self.turnside=None
        if evt.x>self.tlw/2:
            if self.main.orientation and self.current==0:
                pass
            else:
                self.turnside='r'
        elif evt.x<self.tlw/2:
            if not self.main.orientation and self.current==0:
                pass
            else:
                self.turnside='l'
        else: return None
        if self.main.orientation:
            if self.turnside=='l':
                self.turnfwd()
            elif self.turnside=='r':
                self.turnback()
        elif not self.main.orientation:
            if self.turnside=='r':
                self.turnfwd()
            elif self.turnside=='l':
                self.turnback()
    def getentry(self,evt):
        value=self.indexEntry.get()
        try:
            self.current=int(float(value))
            self.indexEntry.delete(0,tk.END)
            self.indexEntry.insert(tk.END,self.current)
        except ValueError:
            self.main.errorMessage('the page number must be an integer')
        self.change()
    def quitwin(self):
        self.root.destroy()
        try:
            if self.pilerrorcounter<0:
                self.main.errorMessage('PIL was not able to detect '
                                       +self.pilerrorcounter+' images')
        except:pass
    def returnroot(self):
        return self.root
    def returncurrent(self):
        return self.current,self.totalpage

if __name__ == '__main__':
    Mainwindow=Mainwindow()