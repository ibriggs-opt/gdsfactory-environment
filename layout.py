import gdsfactory as gf
import component_library as cp
import numpy as np

gf.gpdk.PDK.activate()

""" waveguide parameters """

wg_width = 0.8 #um, waveguide width
bend_radius = 30 #um, bending radius
radius_min = 20 #um, minimum bending radius
wavelength = 1.55 #um
layer = "WG" #name of layer for waveguides
layer_label = "TEXT" #name of layer for labels

CS = gf.cross_section.cross_section(width=wg_width,
                                     offset=0, 
                                     layer=layer, 
                                     sections=None, 
                                     port_names=('o1', 'o2'), 
                                     port_types=('optical', 'optical'), 
                                     bbox_layers=None, bbox_offsets=None, 
                                     cladding_layers=None, cladding_offsets=None, 
                                     cladding_simplify=None, cladding_centers=None, 
                                     radius=bend_radius, radius_min=radius_min, 
                                     main_section_name='_default')

#grating coupler object
gr = cp.grate_coupler(cross_section=CS) 

""" defining test structures """
def MMI_basic_test(width_mmi: float, #width of mmi section
                   length_mmi: float, #length of mmi section
                   include_label: bool = True, #if include device label 
                ) -> gf.Component:
    c = gf.Component()

    gr_array = c << cp.grate_coupler_array(gr=gr,cross_section=CS)
    mmi = c << cp.mmi2x2(width_mmi=width_mmi, length_mmi= length_mmi, cross_section=CS)

    mmi.movex(-length_mmi/2)
    mmi.movey(100.0)

    ports1 = [gr_array.ports[f"o{i}"] for i in [1,2]]
    ports2 = [mmi.ports[f"o{i}"] for i in [2,1]]
    gf.routing.route_bundle(component=c, ports1=ports1, ports2=ports2, cross_section=CS, separation=1)

    ports1 = [gr_array.ports[f"o{i}"] for i in [3,4]]
    ports2 = [mmi.ports[f"o{i}"] for i in [4,3]]
    gf.routing.route_bundle(component=c, ports1=ports1, ports2=ports2, cross_section=CS, separation=1)

    if include_label: 
        label_text = f"w_MMI = {width_mmi}, L_MMI = {length_mmi}"
        lb = c << gf.components.text(text=label_text,
                                size=10,
                                justify="center",
                                layer=layer_label)
        lb.movey(100.0 + width_mmi/2 + 20.0)
        #lb.movex(100.0 + width_mmi/2 + 20.0)

    return c


""" sweep parameters """

MMI_LENGTH = np.arange(20.0,40.1,5.0)
MMI_WIDTH = np.arange(8.0,12.1,0.5)

pitch_x = 1000.0 #um, device pitch in x direction 
pitch_y = 400.0 #um, device pitch in y direction

#array of MMI test objects
MMI_arr = [[None for _ in range(len(MMI_WIDTH))] for _ in range(len(MMI_LENGTH))] #MMI_arr[ilength][iwidth]

MMI_die = gf.Component() #collection of MMI test structures

for iL in range(len(MMI_LENGTH)):
    for iw in range(len(MMI_WIDTH)):
        MMI_arr[iL][iw] = MMI_die << MMI_basic_test(width_mmi=MMI_WIDTH[iw], length_mmi=MMI_LENGTH[iL])

        MMI_arr[iL][iw].movex(pitch_x*iw)
        MMI_arr[iL][iw].movey(pitch_y*iL)


#save gds in gds directory
MMI_die.write_gds("gds files\MMI_basic.gds")

MMI_die.show()