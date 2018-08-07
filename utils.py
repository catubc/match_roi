import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from matplotlib import path

class mark_class():
    
    def __init__(self):
        pass

    def load_mat(self, fname):
        ''' Load matlab dictionary, index into correct structures
        '''
        
        data = sio.loadmat(fname)

        #contour = data['dorsalMaps'][0][0][0]
        self.original = data['dorsalMaps'][0][0][0]
        print (self.original.shape)
        self.new_original = np.zeros((550,550), 'int32') 
        self.new_original[:self.original.shape[0], :self.original.shape[1]]=self.original
        self.original=self.new_original
        
        
        # load contours, names, and sides from file
        temp_contours = data['dorsalMaps'][0][0][12]
        temp_names = data['dorsalMaps'][0][0][13]
        temp_sides = data['dorsalMaps'][0][0][15]

        # make list of contours by area
        self.ROI_contours = []
        for k in range(len(temp_contours)):
            self.ROI_contours.append(data['dorsalMaps'][0][0][12][k][0])

        # mak list of contour names     
        self.ROI_names = []
        for k in range(len(temp_names)):
            self.ROI_names.append(str(data['dorsalMaps'][0][0][13][k][0][0]))

        # make list of contours sides
        self.ROI_contour_sides = []
        for k in range(len(temp_sides)-1):
            self.ROI_contour_sides.append(data['dorsalMaps'][0][0][15][k][0][0])

        # make an image containing all contours for dataset
        #self.img = np.zeros(self.original.shape,'int32')
        self.img = np.zeros((600,600),'int32')
        for p in range(len(self.ROI_contours)):
            for k in range(len(self.ROI_contours[p])):
                self.img[int(self.ROI_contours[p][k][0]),int(self.ROI_contours[p][k][1])]=1

    def mark_ROI(self):
        ''' Function to crop field-of-view of video
        '''
        global ax, fig, coords, cid
        n_pixels = 600

        #Compute pixel locations inside cropped area
        all_pts = []
        # not pythonic; fix this
        for i in range(n_pixels):
            for j in range(n_pixels):
                all_pts.append([i,j])
                
        self.reference=self.original.copy()
        all_pts_reference = []
        for i in range(self.reference.shape[0]):
            for j in range(self.reference.shape[1]):
                all_pts_reference.append([i,j])
        
        mask_save = np.zeros((n_pixels,n_pixels),dtype=np.int8)
        # loop over all ROI_names to be used in alignment
        for k in range(len(self.ROI_names)): 
            coords = []
            
            #fig, ax = plt.subplots(nrows=1,ncols=2, figsize=(20,10))
            fig, ax = plt.subplots(nrows=1,ncols=2)
            mask_save*=0

            # ****** PLOT REFERENCE CONTOR FILLED IN ON RIGHT ********
            area_coords = self.ROI_contours[k]
            p = path.Path(area_coords)
            print (area_coords)
            pts_inside = p.contains_points(all_pts)

            # mark points inside mask 
            idx = np.where(pts_inside==True)[0]
            i_array = np.int32(idx/float(n_pixels))
            j_array = np.int32(idx%n_pixels)     
            print (i_array[:5],j_array[:5])       
            mask_save[i_array,j_array]=True

            # normalize image to only show 0, 1 and 2 values;
            self.img_out = np.ndarray.clip(self.img+2*mask_save, min=0,max=2)
            ax[1].imshow(self.img_out)

            ax[1].set_title("reference mask")
            plt.suptitle("Select: "+self.ROI_contour_sides[k]+ "-"+self.ROI_names[k])
            
            # ********** PLOT RAW IMAGE TO BE ANNOTATED ********
            self.reference=self.original.copy()
            ax[0].imshow(self.reference)#, vmin=0.0, vmax=0.02)
            
            # connect figure to call back for coordinate selection
            cid = fig.canvas.mpl_connect('button_press_event', self.on_click)
            plt.show(block=True)
            
            # print selected ROI filled in
            coords = np.vstack(coords)
            print (coords)
       
            # ********** REPLOT THE SELECTED ROI FILLED IN ************
            p2 = path.Path(coords)
            pts_inside1 = p2.contains_points(all_pts_reference)
            idx1 = np.where(pts_inside1==True)[0]
            print (idx1)
                        
            # mark points inside mask 
            img_mask = np.zeros(self.reference.shape,'int32')
            i_array = np.int32(idx1/float(self.reference.shape[0]))
            j_array = np.int32(idx1%self.reference.shape[1])
            print (i_array[:5],j_array[:5])
            img_mask[i_array,j_array]=np.max(self.reference)
            
            # replot everything
            fig, ax = plt.subplots(nrows=1,ncols=2)
            ax[0].imshow(img_mask+self.reference,vmin=0,vmax=np.max(self.reference))
            ax[1].imshow(self.img_out)
            plt.show()
            
        return x_coords, y_coords

    def on_click(self, event):
        ''' Mouse click function that catches clicks and plots them on top of existing image
        '''
        
        if event.inaxes is not None:
            print (event.ydata, event.xdata)
            coords.append((event.ydata, event.xdata))
            #for j in range(len(coords)):
            for k in range(2):
                for l in range(2):
                    self.reference[int(event.ydata)-1+k,int(event.xdata)-1+l]=np.max(self.reference)

            ax[0].imshow(self.reference)
            fig.canvas.draw()
        else:
            print ('Exiting')
            plt.close()
            fig.canvas.mpl_disconnect(cid)
