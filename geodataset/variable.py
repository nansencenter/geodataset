import numpy as np

#from previous code
def exchange_names(vname, variables):

    if vname in variables:
        return vname

    lists = []

    # ice conc alt names
    lists.append(['ficem','fice','ice_conc','icec',\
                   'concentration','sea_ice_concentration',\
                   'ice fraction','sic',
                   'Concentration'])

    # ice thick alt names
    lists.append(['hicem','hice','ice_thick','icetk',\
                   'sea_ice_thickness','thickness',\
                   'sit', 'analysis_thickness',
                   'Thickness'])

    # floe size alt names
    lists.append(['dfloe','dmax','Dfloe','Dmax'])

    # H_s alt names
    lists.append(['swh','Hs','hs'])

    for names in lists:
        if vname in names:
            for vbl in names:
                if vbl in variables:
                    return vbl

    raise ValueError(vname+' not in variable list')



#from previous code
class var_object:
    """
    vbl=var_object(vals,mask_in=None,extra_atts=None):
    *vals is an array or masked array
    *mask_in is a bool array
    *xtra_atts=[attlist,attvals] - attlist and attvals are lists
    of attribute names and values for output
    *vbl.values is a masked array
     - also has shape and ndim att's, and min,max methods
    """
    def __init__(self,vals,mask_in=None,extra_atts=None):

        if extra_atts is not None:
            attlist,attvals = extra_atts
            for i,att in enumerate(attlist):
                setattr(self, att, attvals[i])

        self.shape  = vals.shape
        self.ndim    = vals.ndim

        # create masked array
        if hasattr(vals,'mask'):
            # already a masked array
            if mask_in is None:
                # don't need to change mask
                self.values = vals
            else:
                # if additional mask is passed in,
                # take union of masks
                mask = np.logical_or(vals.mask,mask_in)
                self.values = np.ma.array(vals.data, mask=mask)
        else:
            # convert to masked array
            # - check for NaNs
            mask  = np.logical_not(np.isfinite(vals))

            if mask_in is not None:
                # if additional mask is passed in,
                # take union of masks
                mask = np.logical_or(mask, mask_in)

            self.values = np.ma.array(vals,mask=mask)

    # activate self[:,:]
    def __getitem__(self, indexes):
        return self.values.__getitem__(indexes)

    def min(self):
        return self.values.min()

    def max(self):
        return self.values.max()
