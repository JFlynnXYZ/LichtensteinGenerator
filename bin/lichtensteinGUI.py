import Tkinter as tk
import tkColorChooser 
import ttk
import tkMessageBox as tkMsgBox
import tkFileDialog as tkFDialog
import Queue
import threading
import os
import platform
from functools import partial
from PIL import Image
try:
    from PIL import ImageTk
except ImportError:
    ImageTk = False
    
try:
	import winsound
except ImportError:
	def play_sound():
		pass
else:
	def play_sound():
		winsound.PlaySound("SystemAsterisk",
									winsound.SND_ALIAS|winsound.SND_ASYNC)
import lichtenstein as li
import halftoning as ht
from colour import rgb2hex, hex2rgb
SMALL_MONITOR_W, SMALL_MONITOR_H = 1280, 1024


class LichThread(threading.Thread):
    
    
    def __init__(self, queue, img, val):
        threading.Thread.__init__(self)
        self.queue = queue
        self.img = img
        self.values = val
        
        
    def run(self):
        val = self.values
        lich = li.lichtenstein(self.img, val[0], float(val[1]), int(val[2]), 
                               float(val[3]), float(val[4]), float(val[5]), 
                               val[6], int(val[7]), val[8], float(val[9]), 
                               int(val[10])+1)
        self.queue.put("The Lichtenstein has finished generating")
        self.queue.put(lich)


class ImageViewer(tk.Canvas):
    
    def __init__(self, master, imgLoc=None, cnf={}, **kw):
        tk.Canvas.__init__(self, master, cnf, **kw)
        self['bg'] = 'grey'
        self.zoomPer = 1
        self.maxZoom = 32
        self.minZoom = 0.0013
        
        if imgLoc != None:
            self.set_image(imgLoc)
        else:
            self.set_image()
    
    def set_image(self, imgLoc=None):
        if imgLoc != None:
            self._image = Image.open(imgLoc)
        else:
            self._image = Image.new('RGB', (512,512), 'white')
        if ImageTk != False:
            self.photo = ImageTk.PhotoImage(self._image)
            self.redraw()
            self.activate_zoom()
            self.bind("<Enter>", self.activate_zoom)
            self.bind("<Leave>", self.deactivate_zoom)
        
            self.bind("<Expose>", self.redraw)
        else:
            pass

        
    def fit_to_canvas(self):
        cSize = self.winfo_width(), self.winfo_height()
        
        size = self._image.size
        
        differ = cSize[0] - size[0], cSize[1] - size[1]
        
        if differ[0] < differ[1]:
            self.zoomPer = float(cSize[0]) / size[0]
        else:
            self.zoomPer = float(cSize[1]) / size[1]
            
        finalSize = int(self.zoomPer*size[0])-10, int(self.zoomPer*size[1])-10
        self.photo = ImageTk.PhotoImage(self._image.resize(finalSize))
        self.redraw()
        
    def reset_zoom(self):
        self.set_zoom(1)
        
    def set_zoom(self, zoom):
        self.zoomPer = zoom
        self.crop()
        
    def zoom(self, event=None):
        if event.delta > 0:
            if self.zoomPer < self.maxZoom:
                self.zoomPer *= 1.1
                self.crop(event)
        elif event.delta < 0:
            if self.zoomPer > self.minZoom and (self.photo.width() >=1 or
                                                self.photo.height() >=1):
                self.zoomPer *= 0.9
                self.crop(event)
                
                
    def crop(self, event=None):
        cSize = self.winfo_width(), self.winfo_height()
        
        size = int(round(self._image.size[0]*self.zoomPer)), \
               int(round(self._image.size[1]*self.zoomPer))
        
        
        if size[0] > cSize[0] and size[1] > cSize[1]:
            if event != None:
                canX, canY = self.canvasx(event.x), self.canvasy(event.y)
            else:
                canX, canY = cSize[0]/2, cSize[1]/2
            self.photo = ImageTk.PhotoImage(self._image.resize(size))
            self.redraw(point=(cSize[0]-canX, cSize[1]-canY))
        else:
            self.photo = ImageTk.PhotoImage(self._image.resize(size))
            self.redraw()
            
        
    def activate_zoom(self, event=None):
        self.bind_all("<MouseWheel>", self.zoom)
        self._root().focus()

    def deactivate_zoom(self, event=None):
        self.unbind_all("<MouseWheel>")
        
    def redraw(self, event=None, point='centre'):
        try:
            self.delete(self.cBorder)
            self.delete(self.cImg)
        except AttributeError:
            pass
        
        if point == 'centre':
            pp = self.winfo_width()/2, self.winfo_height()/2
        else:
            pp = point
        
        bdCoords = (pp[0]-self.photo.width()/2-1, pp[1]-self.photo.height()/2-1,
                    pp[0]+self.photo.width()/2, pp[1]+self.photo.height()/2)
        
        self.cImg = self.create_image(*pp, image=self.photo)
        self.cBorder = self.create_rectangle(*bdCoords, fill=None, 
                                                    outline='black')
        self.update()
        
    def change_image(self, pilImg):
        self._image = pilImg
        if ImageTk != False:
            self.photo = ImageTk.PhotoImage(self._image)
            if self.photo.width() > self.winfo_width() or \
               self.photo.height() > self.winfo_height():
                self.fit_to_canvas()
            else:
                self.redraw()
        
    def change_image_dir(self, imgLoca):
        try:
            pilImg = Image.open(imgLoca)
            self.change_image(pilImg)
        except IOError as e:
            tkMsgBox.showerror('Invalid File', '{0}.'.format(e.args[0].capitalize()))
        
    def get(self):
        return self._image
        
    def show_image(self):
        if platform.system() == 'Windows':
            self._image.show()
        else:
            self._image.show(command='display')
			
			
class ColourTable(tk.Canvas):
    
    
    def __init__(self, master, cnf={}, **kw):
        tk.Canvas.__init__(self, master, cnf, **kw)
        self['bg'] = 'grey'
        self.colGrid = [[] for _ in xrange(16)]
        self.colGridLength = 0
        self.maxValues = 256
        
        self.selectCol = None
        
        
        self.bind("<Enter>", self.activate_select)
        self.bind("<Leave>", self.deactivate_select)
        
    def _add_colour(self, colour="#777777"):
        if self.colGridLength >= self.maxValues:
            play_sound()
        else:
            for x in xrange(len(self.colGrid)):
                y = len(self.colGrid[x])
                if y < 16:
                    self.colGrid[x].append(self._draw_colour(x,y,colour))
                    self.colGridLength += 1
                    break
            else:
                play_sound()
        
        
    def _draw_colour(self, x,y, colour):
        boxX, boxY = int(self.winfo_height()/16.0), int(self.winfo_width()/16.0)
        coords = boxX*x+2, boxY*y+2, boxX*(x+1)+2, boxY*(y+1)+2
        return self.create_rectangle(coords, fill=colour, outline='black')
        
    def _remove_colour(self, x,y):
        try:
            self.delete(self.colGrid[x][y])
            del(self.colGrid[x][y])
            self.colGridLength -= 1
            return True
        except IndexError:
            return False
            
    def reduce_colours(self, nCols):
        remNCols = self.colGridLength - nCols
        for x in xrange(len(self.colGrid)-1,-1,-1):
                for y in xrange(len(self.colGrid)-1,-1,-1):
                    if remNCols <= 0:
                        break
                    else:
                        if self._remove_colour(x,y):
                            remNCols -=1
        self.redraw()
                        
                        
    def redraw(self, *args):
        for x in xrange(16):
            for y,boxID in enumerate(self.colGrid[x]):
                colour = self.itemcget(boxID, 'fill')
                self.delete(self.colGrid[x][y])
                self.colGrid[x][y] = self._draw_colour(x,y,colour)
                try:
                    if self.selectCol[0] == boxID:
                        self.switch_select_colour(self.colGrid[x][y])
                except TypeError:
                    pass
        self.update()
        
    def activate_select(self, event=None):
        self.bind_all("<Button-1>", self.select_colour)
        self.bind_all("<Double-Button-1>", self.change_colour)
        
    def deactivate_select(self, event=None):
        self.unbind_all("<Button-1>")
        self.unbind_all("<Double-Button-1>")
        
    def change_colour(self, event):
        if self.selectCol != None:
            initial = self.itemcget(self.selectCol[0], 'fill')
            _, hx = tkColorChooser.askcolor(initialcolor=initial)
            if hx != None:
                self.itemconfig(self.selectCol[0], fill=hx)
                self.redraw()
                
    def remove_selected_colour(self):
        if self.selectCol != None:
            for x,colList in enumerate(self.colGrid):
                try:
                    y = colList.index(self.selectCol[0])
                    break
                except ValueError:
                    pass
            else:
                y = None
            if y != None:
                self._remove_colour(x,y)
                self.redraw()
                self.delete(self.selectCol[1])
                self.selectCol = None
                
    def add_specific_colour(self):
        if self.colGridLength >= self.maxValues:
            play_sound()
        else:
            _, hx = tkColorChooser.askcolor()
            if hx != None:
                self._add_colour(hx)
        
    def switch_select_colour(self, cur):
        if cur == None:
            self.clear_select()
        else: 
            if self.selectCol != None:
                self.clear_select()
            bbox = self.bbox(cur)
            self.selectCol = cur, self.draw_select(bbox)
            
    def clear_select(self):
        if self.selectCol != None:
            self.delete(self.selectCol[1])
            self.selectCol = None
            
    def draw_select(self, bbox):
        bbox2 = bbox[0]+2,bbox[1]+2, bbox[2]-2,bbox[3]-2
        highlight = self.create_rectangle(bbox2, fill=None, outline='white')
        return highlight
        
        
    def select_colour(self, event):
        canX, canY = self.canvasx(event.x), self.canvasy(event.y)
        box = self.find_overlapping(canX, canY, canX, canY)
        if len(box) > 0:
            self.switch_select_colour(box[0])
        else:
            self.switch_select_colour(None)
            
            
    def colCBox_validate(self, curVal):
        if not curVal.isdigit() and curVal != '':
            play_sound()
            return False
        else:
            return True
        
    def colCBox_check(self, strVar, *args):
        curVal = strVar.get()
        if curVal == '':
            curVal = 0
            
        if int(curVal) < self.maxValues and int(curVal) < self.colGridLength:
                if tkMsgBox.askyesno("Colour Table", 
                                      "Are you sure you want to reduce the " \
                                      "amount of colours? If you do, colours" \
                                      " will be removed from the table."):
                    self.maxValues = int(curVal)
                    self.reduce_colours(self.maxValues)
                else:
                    strVar.set(self.maxValues)
        else:
            self.maxValues = int(curVal)
            
    def get(self):
        colours = []
        for colList in self.colGrid:
            for box in colList:
                colours.append(hex2rgb(self.itemcget(box, 'fill')))
        return colours
                
    def set(self, colours):
        self.reduce_colours(0)
        for col in colours:
            hx = rgb2hex(col[0],col[1],col[2])
            self._add_colour(hx)
        self.update()
        
    def set_max_colours(self, nCols):
        self.maxValues = nCols
        
        
class ColourSwatch(tk.Canvas):
    
    
    def __init__(self, master, cnf={}, **kw):
        tk.Canvas.__init__(self, master, cnf, **kw)

        self.bind("<Enter>", self.activate_select)
        self.bind("<Leave>", self.deactivate_select)
        
        
    def activate_select(self, event=None):
        self.bind_all("<Double-Button-1>", self.change_colour)
        
        
    def deactivate_select(self, event=None):
        self.unbind_all("<Double-Button-1>")
        
        
    def change_colour(self, event):
        _, hx = tkColorChooser.askcolor(initialcolor=self['bg'])
        if hx != None:
            self['bg'] = hx
            
            
    def get(self):
        return hex2rgb(self['bg'])
    
    def set(self, col):
        hx = rgb2hex(col[0],col[1],col[2])
        self['bg'] = hx
            
class ProgressWindow(tk.Toplevel):
    
    
    def __init__(self, master=None, text='Completing...'):
        tk.Toplevel.__init__(self, master)
        self.title('Progress...')
        self.geometry("250x50")
        self.resizable('false','false')
        self.transient(self.master)
        self.disable_parent()
        self.frame = tk.Frame(self)
        self.frame.pack(fill='both', expand=1)
        
        tk.Label(self.frame, text=text).pack()
        self.prgBar = ttk.Progressbar(self.frame, mode='indeterminate')
        self.prgBar.pack(fill='x', padx=20)
        self.protocol('WM_DELETE_WINDOW', self.stop_close)
        self.centre_geometry()
        
    def disable_parent(self):
        if platform.system() == 'Windows':
            self.master.attributes("-disabled",1)
        else:
            self.grab_set()
        
    def enable_parent(self):
        if platform.system() == 'Windows':
            self.master.attributes("-disabled",0)
        else:
            self.grab_release()
        self.master.focus_force()
        
    def stop_close(self):
        tkMsgBox.showwarning('Warning!',
                                 'The pending action has not finished yet')
        
    def centre_geometry(self):
        self.update_idletasks()
        w, h = SMALL_MONITOR_W, SMALL_MONITOR_H
        rootsize = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w/2 - rootsize[0]/2
        y = h/2 - rootsize[1]/2
        self.geometry("%dx%d+%d+%d" % (rootsize + (x, y)))

    def start(self):
        self.prgBar.start()
        
    def stop(self):
        self.prgBar.stop()
        
    def close(self, message):
        self.prgBar.stop()
        tkMsgBox.showinfo('Completed', message)
        self.enable_parent()
        self.destroy()
        
class App(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Lichtenstein Art Generator by Jonathan Flynn :: jfdesigner.co.uk')
        self.minsize(1024, 875)
        
        self.QUANT_BITS = [2,4,8,16,32,64,128,256]
        test = ((83,31,72),(255,241,191),(38,22,184),(233,95,113),(190,159,163))
        self.PRESETS = {'Default': {'qtNCols': 8, 'qtNewCols': li.DEFAULT_COLOURS, 
                                    'qtSigma': 4, 'htBox': 8, 
                                    'htColour': ht.AVERAGE_COLOUR_ON_WHITE, 
                                    'htCRatio': 1, 'edSigma': 1.4, 'edThresH': 0.2, 
                                    'edThresL': 0.1, 'edColour': (0,0,0), "aalias":2},
                        'Cool':    {'qtNCols': 12, 'qtNewCols': test, 
                                    'qtSigma': 6, 'htBox': 15, 
                                    'htColour': ht.AVERAGE_COLOUR_ON_BLACK, 
                                    'htCRatio': 1.1, 'edSigma': 1.8, 'edThresH': 0.2, 
                                    'edThresL': 0.1, 'edColour': (125,0,0), "aalias": 2}
                        }
                        
        self.fileOptSave = {'defaultextension': '.png', 
                        'filetypes': [('All files', '.*'), ('BMP', '.bmp'),
                                      ('JPEG', '.jpg'), ('PNG', '.png') ],
                        'initialdir': os.getenv('USERPROFILE'),
                        'initialfile': 'lichtenstein.png',
                        'title': 'Save As'}
        self.fileOptOpen = self.fileOptSave.copy()
        self.fileOptOpen['title'] = 'Open Image'
        self.fileOptOpen['filetypes'] = [('All Images', ('.bmp','.jpg','.png')),
										 ('BMP', '.bmp'),('JPEG', '.jpg'), 
                                         ('PNG', '.png'), ('All files', '.*')]
        self.fileOptOpen['initialfile'] = ''
        if platform.system() == 'Linux':
            self.fileOptSave['filetypes']
        self.PRESET_NAMES = self.PRESETS.keys()
        
        self.create_widgets()
        
        self.centre_geometry()
        if ImageTk == False:
            tkMsgBox.showerror('Import Error', 'The linux machines don\'t allow for '
                               'image previews due to the missing ImageTk module.'
                               ' For the best result run the executable on a Windows machine')
        
    def centre_geometry(self):
        self.update_idletasks()
        w, h = SMALL_MONITOR_W, SMALL_MONITOR_H
        rootsize = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w/2 - rootsize[0]/2
        y = h/2 - rootsize[1]/2
        self.geometry("%dx%d+%d+%d" % (rootsize + (x, y)))
        
    def int_field_validate(self, curVal):
        if curVal != '':
            try:
                int(curVal)
                return True
            except ValueError:
                play_sound()
                return False
        else:
            return True
        
    def float_field_validate(self, curVal):
        if curVal != '':
            try:
                float(curVal)
                return True
            except ValueError:
                play_sound()
                return False
        else:
            return True
        
    def preset_change(self, strVar, *args):
        chosenPreset = strVar.get()
        self.colTable.set_max_colours(256)
        for arg,value in self.PRESETS[chosenPreset].iteritems():
            if arg == 'htColour':
                if value[0] == ht.AVERAGE_COLOUR:
                    self.parameters[arg][0].set((128,128,128))
                    self.parameters[arg][2].set(True)
                else:
                    self.parameters[arg][0].set(value[0])
                    self.parameters[arg][2].set(False)
                self.parameters[arg][1].set(value[1])
            elif arg == 'qtNCols':
                self.colTable.set_max_colours(value)
                self.parameters[arg].set(value)
            else:
                self.parameters[arg].set(value)
                
    def process_queue(self):
        try:
            msg = self.queue.get(0)
            self.prgWindow.close(msg)
            lichImg = self.queue.get(0)
            self.imgViewGenr.change_image(lichImg)
            if ImageTk == False:
                lichImg.show()
        except Queue.Empty:
            self.after(100, self.process_queue)
        
                
    def setup_lichtenstein(self):
        p = self.parameters
        img = self.imgViewOrig._image
        if p['htColour'][2].get() == True:
            htColour = ht.AVERAGE_COLOUR, p['htColour'][1].get()
        else:
            htColour = p['htColour'][0].get(), p['htColour'][1].get()
            
        values = (p['qtNewCols'].get(), p['qtSigma'].get(), p['qtNCols'].get(), 
                  p['edSigma'].get(), p['edThresH'].get(), p['edThresL'].get(), 
                  p['edColour'].get(), p['htBox'].get(), htColour, 
                  p['htCRatio'].get(), p['aalias'].get())
        
        self.prgWindow = ProgressWindow(self, 'Generating Lichtenstein Art...')
        
        if values[2] == '' or int(values[2]) < 2 or int(values[2]) > 256:
            tkMsgBox.showerror('Must have 2 or more colours and be less than 256')
        elif values[7] == '':
            self.parameters['htBox'].set('0')
            values[7] = 0
        elif values[4] == '' or float(values[4]) < 0:
            tkMsgBox.showerror('Higher Edge Threshold should be higher than zero')
        elif values[5] == '' or float(values[5]) < 0:
            tkMsgBox.showerror('Lower Edge Threshold should be higher than zero')
        elif values[10] == '' or int(values[10]) < 0:
            tkMsgBox.showerror('Anti alias should be higher than zero')
        else:
            self.prgWindow.start()
            self.queue = Queue.Queue()
            LichThread(self.queue, img, values).start()
            self.after(10, self.process_queue)
        
    def save_image(self):
        filename = tkFDialog.asksaveasfilename(**self.fileOptSave)
        if filename != '':
            lich = self.imgViewGenr.get()
            try:
                lich.save(filename)
                tkMsgBox.showinfo('Save Complete', 'The file was saved correctly')
            except Exception as e:
                tkMsgBox.showerror('Save Failed', 
                                   'The file was saved incorrectly: {0}'.format(e.args[0]))
            
    def change_image(self):
        filename = tkFDialog.askopenfilename(**self.fileOptOpen)
        if filename != '':
            self.imgViewOrig.change_image_dir(filename)
            self.imgViewGenr.change_image_dir(filename)
            
        
    def create_widgets(self):
        intVCMD = (self.register(self.int_field_validate), '%P')
        floatCMD = (self.register(self.float_field_validate), '%P')
        self.parameters = {}
        
        self.nb = ttk.Notebook(self)
        self.nb.grid(sticky='nesw')
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.imgFrameOrig = tk.Frame(self.nb)
        self.imgViewOrig = ImageViewer(self.imgFrameOrig)
        self.imgViewOrig.pack(fill='both', expand=1)
        self.origOptFrame = tk.Frame(self.imgFrameOrig, height=25)
        self.origOptFrame.pack(fill='x')
        self.origResetBut = tk.Button(self.origOptFrame, text='100% Zoom', 
                                     command=self.imgViewOrig.reset_zoom)
        self.origResetBut.pack(side='left', padx=6)
        self.origFitBut = tk.Button(self.origOptFrame, text='Fit to Canvas', 
                                     command=self.imgViewOrig.fit_to_canvas)
        self.origFitBut.pack(side='left', padx=6)
        self.origChangeBut = tk.Button(self.origOptFrame, text='Change Image',
                                       command=self.change_image)
        self.origChangeBut.pack(side='left', padx=6)
        self.genrShowBut = tk.Button(self.origOptFrame, text='Show Image',
                                     command=self.imgViewOrig.show_image)
        self.genrShowBut.pack(side='left', padx=6)
    
        if ImageTk == False:
            self.origResetBut['state'] = 'disabled'
            self.origFitBut['state'] = 'disabled'
        
        self.imgFrameGenr = tk.Frame(self.nb)
        self.imgViewGenr = ImageViewer(self.imgFrameGenr)
        self.imgViewGenr.pack(fill='both', expand=1)
        self.genrOptFrame = tk.Frame(self.imgFrameGenr, height=25)
        self.genrOptFrame.pack(fill='x')
        self.genrResetBut = tk.Button(self.genrOptFrame, text='100% Zoom', 
                                     command=self.imgViewGenr.reset_zoom)
        self.genrResetBut.pack(side='left', padx=6)
        self.genrFitBut = tk.Button(self.genrOptFrame, text='Fit to Canvas', 
                                     command=self.imgViewGenr.fit_to_canvas)
        self.genrFitBut.pack(side='left', padx=6)
        self.genrChangeBut = tk.Button(self.genrOptFrame, text='Change Image',
                                       command=self.change_image)
        self.genrChangeBut.pack(side='left', padx=6)
        self.genrShowBut = tk.Button(self.genrOptFrame, text='Show Image',
                                       command=self.imgViewGenr.show_image)
        self.genrShowBut.pack(side='left', padx=6)
        
        if ImageTk == False:
            self.genrResetBut['state'] = 'disabled'
            self.genrFitBut['state'] = 'disabled'
        

        self.nb.add(self.imgFrameOrig, text='Original')
        self.nb.add(self.imgFrameGenr, text='Result')
        self.nb.select(1)
        
        
        self.optFrame = tk.Frame(self, bd=1, relief='ridge', width=300)
        self.optFrame.grid(column=1, row=0, sticky='nesw')
        self.optFrame.grid_propagate(0)
        self.optFrame.columnconfigure(0, weight=1)
        self.optFrame.rowconfigure(0, pad=20)
        self.optFrame.rowconfigure((1,2,3), pad=10)
        
        
        self.preFrame = tk.Frame(self.optFrame)
        self.preFrame.grid(sticky='nesw', padx=6, pady=6)
        self.preFrame.grid_propagate(0)
        self.preFrame.columnconfigure(0, pad=25)
        self.preFrame.columnconfigure(1, weight=1)
        self.preFrame.rowconfigure(0, weight=1)
        
        tk.Label(self.preFrame, text='Presets:').grid(sticky='e')
        self.preStrVar = tk.StringVar()
        self.preCBox = ttk.Combobox(self.preFrame, values=self.PRESET_NAMES, width=25,
                                    state='readonly', textvariable=self.preStrVar)
        self.preCBox.grid(column=1, row=0, sticky='ew', padx=6)
        preCMD = partial(self.preset_change, self.preStrVar)
        self.preStrVar.trace('w', preCMD)
        
        
        self.quaFrame = tk.LabelFrame(self.optFrame, text='Quantize')
        self.quaFrame.grid(sticky='nesw', padx=6, pady=6, column=0, row=1)
        self.quaFrame.columnconfigure(0, pad=25)
        self.quaFrame.columnconfigure(1, weight=1)
        
        tk.Label(self.quaFrame, text='Colours:').grid(sticky='e')
        self.colCBox = ttk.Combobox(self.quaFrame, values=self.QUANT_BITS, width=25,
                                    validate='key')
        self.colCBox.grid(column=1, row=0, sticky='ew', padx=6)
        
        
        self.colLFrame = tk.LabelFrame(self.quaFrame, text='Colour Table')
        self.colLFrame.grid(column=0, columnspan=2, row=2, padx=6)
        self.colLFrame.columnconfigure(0, weight=1)
        self.colLFrame.columnconfigure(1, weight=1)
        self.colLFrame.rowconfigure(0, weight=1)
        
        self.colTable = ColourTable(self.colLFrame, width=257, height = 257)
        self.colTable.grid(columnspan=2)
        self.parameters['qtNewCols'] = self.colTable
        
        vcmd = (self.register(self.colTable.colCBox_validate), '%P')
        self.colCBoxStrVar = tk.StringVar()

        
        self.colCBox['textvariable'] = self.colCBoxStrVar
        self.colCBox['validatecommand'] = vcmd
        self.colCBox.bind('<Return>', partial(self.colTable.colCBox_check, self.colCBoxStrVar))
        self.colCBox.bind('<<ComboboxSelected>>', partial(self.colTable.colCBox_check, self.colCBoxStrVar))
        self.parameters['qtNCols'] = self.colCBoxStrVar
        
        self.addColBut = tk.Button(self.colLFrame, text='Add Colour', 
                                   command=self.colTable.add_specific_colour)
        self.addColBut.grid(row=1, sticky='nesw')
        
        self.delColBut = tk.Button(self.colLFrame, text='Remove Colour', 
                                   command=self.colTable.remove_selected_colour)
        self.delColBut.grid(row=1, column=1, sticky='nesw')
        
        tk.Label(self.quaFrame, text='Denoise Amount:').grid(row=3, sticky='es')
        self.denColScale = tk.Scale(self.quaFrame, from_=1.0, to=10.0, 
                                    orient='horizontal', resolution=0.1)
        self.denColScale.grid(row=3, column=1, sticky='ew', padx=6)
        self.parameters['qtSigma'] = self.denColScale
        
        
        self.halFrame = tk.LabelFrame(self.optFrame, text='Halftoning')
        self.halFrame.grid(sticky='nesw', padx=6, pady=6, column=0, row=2)
        self.halFrame.columnconfigure(0, pad=25)
        self.halFrame.columnconfigure((1,2), weight=1)
        
        
        tk.Label(self.halFrame, text='Box Width/Height:').grid(sticky='e')
        self.boxStrVar = tk.StringVar() 
        self.boxEntry = tk.Entry(self.halFrame, validate='key', 
                                 validatecommand=intVCMD, textvariable=self.boxStrVar)
        self.boxEntry.grid(column=1, row=0, sticky='ew', padx=6, columnspan=2)
        self.parameters['htBox'] = self.boxStrVar
        
        tk.Label(self.halFrame, text='Circle Ratio:').grid(sticky='es') 
        self.cRatScale = tk.Scale(self.halFrame, from_=0.01, to=2.0, 
                                    orient='horizontal', resolution=0.01)
        self.cRatScale.grid(column=1, row=1, sticky='ew', padx=6, columnspan=2)
        self.parameters['htCRatio'] = self.cRatScale
        
        tk.Label(self.halFrame, 
                 text='Foreground/\nBackground Colour:', 
                 justify='right').grid(column=0, row=2, sticky='e')  
        self.fgCol = ColourSwatch(self.halFrame, bg='grey', bd=1, height=25, 
                                    width=25, relief='raised')
        self.fgCol.grid(column=1, row=2, sticky='ew', padx=6)
        self.bgCol = ColourSwatch(self.halFrame, bg='grey', bd=1, height=25, 
                                    width=25, relief='raised')
        self.bgCol.grid(column=2, row=2, sticky='ew', padx=6)
        
        self.avgColIntVar = tk.IntVar()
        self.avgColCBut = tk.Checkbutton(self.halFrame, variable=self.avgColIntVar,
                                         text='Foreground Average Colour')
        self.avgColCBut.grid(column=0, row=3, columnspan=3, sticky='e')
        
        self.parameters['htColour'] = (self.fgCol, self.bgCol, self.avgColIntVar)
        
        self.edgFrame = tk.LabelFrame(self.optFrame, text='Canny Edge Detect')
        self.edgFrame.grid(sticky='nesw', padx=6, pady=6, column=0, row=3)
        self.edgFrame.columnconfigure(0, pad=25)
        self.edgFrame.columnconfigure(1, weight=1)
        
        tk.Label(self.edgFrame, text='Denoise Amount:').grid(sticky='es')
        self.denEdgScale = tk.Scale(self.edgFrame, from_=1.0, to=10.0, 
                                    orient='horizontal', resolution=0.1,)
        self.denEdgScale.grid(row=0, column=1, sticky='ew', padx=6)
        self.parameters['edSigma'] = self.denEdgScale
        
        tk.Label(self.edgFrame, 
                 text='High Edge Threshold:').grid(column=0, row=1, sticky='e') 
        self.edgThHiStrVar = tk.StringVar()
        self.edgThHiEntry = tk.Entry(self.edgFrame, validate='key', 
                                 validatecommand=floatCMD, 
                                 textvariable=self.edgThHiStrVar)
        self.edgThHiEntry.grid(column=1, row=1, sticky='ew', padx=6)
        self.parameters['edThresH'] = self.edgThHiStrVar
        
        tk.Label(self.edgFrame, 
                 text='Low Edge Threshold:').grid(column=0, row=2, sticky='e')   
        self.edgThLoStrVar = tk.StringVar() 
        self.edgThLoEntry = tk.Entry(self.edgFrame, validate='key', 
                                 validatecommand=floatCMD, 
                                 textvariable=self.edgThLoStrVar)
        self.edgThLoEntry.grid(column=1, row=2, sticky='ew', padx=6)
        self.parameters['edThresL'] = self.edgThLoStrVar
        
        tk.Label(self.edgFrame, text='Edge Colour:').grid(column=0, row=3, 
                                                          sticky='e')  
        self.edgCol = ColourSwatch(self.edgFrame, bg='grey', bd=1, height=25, 
                                    width=25, relief='raised')
        self.edgCol.grid(column=1, row=3, sticky='ew', padx=6)
        self.parameters['edColour'] = self.edgCol
        
        
        self.aaliasFrame = tk.LabelFrame(self.optFrame, text='Anti-aliasing')
        self.aaliasFrame.grid(sticky='nesw', padx=6, pady=6, column=0, row=4)
        self.aaliasFrame.columnconfigure(0, pad=25)
        self.aaliasFrame.columnconfigure(1, weight=1)
        
        tk.Label(self.aaliasFrame, text='Anti-alias Amount:').grid(sticky='e')
        self.aaliasStrVar = tk.StringVar()
        self.aaliasEntry = tk.Entry(self.aaliasFrame, validate='key', 
                                    validatecommand=intVCMD, 
                                    textvariable=self.aaliasStrVar)
        self.aaliasEntry.grid(column=1, row=0, sticky='ew', padx=6, pady=6)
        self.parameters['aalias'] = self.aaliasStrVar
        
        self.genSaveFrame = tk.Frame(self.optFrame, bg='blue')
        self.genSaveFrame.grid(sticky='nesw', padx=6, pady=6, column=0, row=5)
        self.genSaveFrame.columnconfigure((0,1), weight=1)
        
        self.genBut = tk.Button(self.genSaveFrame, text='Generate', width=25,
                                command=self.setup_lichtenstein)
        self.genBut.grid(sticky='nesw')
        self.saveBut = tk.Button(self.genSaveFrame, text='Save', width=25, 
                                 command=self.save_image)
        self.saveBut.grid(sticky='nesw', row=0, column=1)
        
        self.preCBox.current(0)
        
        self.after_idle(self.change_image)
        
if __name__ == '__main__':
    root = App()
    root.mainloop()
