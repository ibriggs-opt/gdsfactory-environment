""" library of components used in layout """

import gdsfactory as gf

def straight(length: float, 
             width: float, 
             layer=(1, 0),
             ) -> gf.Component:
    c = gf.Component()
    c.add_polygon([(0, 0), (length, 0), (length, width), (0, width)], layer=layer)
    c.add_port(
        name="o1", center=[0, width / 2], width=width, orientation=180, layer=layer
    )
    c.add_port(
        name="o2", center=[length, width / 2], width=width, orientation=0, layer=layer
    )
    return c

def mmi2x2(width_mmi: float, #width of MMI
           length_mmi: float, #length of MMI
           width_taper: float = 1.0, #width of taper
           length_taper: float = 5.0, #length of taper
           gap_mmi: float = 0.5, #gap between inputs and outputs
           cross_section = "strip", 
           ) -> gf.Component:
    
    c = gf.components.mmi2x2(width_taper=width_taper, length_taper=length_taper, length_mmi=length_mmi, width_mmi=width_mmi, gap_mmi=gap_mmi, cross_section=cross_section).copy()
    return c


def loopback( pitch: float = 127.0,
             length: float = 50, 
             cross_section = "strip",
             ) -> gf.Component:
    xs = gf.get_cross_section(cross_section)
    c = gf.Component()
    wvgd1 = c << gf.components.straight(length=length, cross_section=cross_section)
    wvgd2 = c << gf.components.straight(length=length, cross_section=cross_section)

    wvgd1.rotate(90)
    wvgd2.rotate(90)
    wvgd2.movex(pitch)

    gf.routing.route_single(c, wvgd1.ports["o2"], wvgd2.ports["o2"], radius=xs.radius, cross_section=cross_section)

    c.add_port("o1", port=wvgd1.ports["o1"])
    c.add_port("o2", port=wvgd2.ports["o1"])

    return c

def grate_coupler( n_periods: int = 30, #number of periods
                  neff: float = 2.6, #effective index, 
                  taper_length: float = 16.6, #length of taper section,
                  taper_angle: float = 40.0, #angle for taper, degrees
                  wavelength: float = 1.55, #wavelength in um, 
                  fiber_angle: float = 10.0, #coupling fiber angle in degrees
                cross_section = "strip",
            ) -> gf.Component:
    c = gf.components.grating_coupler_elliptical(polarization='te', taper_length=taper_length, taper_angle=taper_angle, wavelength=wavelength, fiber_angle=fiber_angle, grating_line_width=0.343, neff=2.638, nclad=1.443, n_periods=n_periods, big_last_tooth=False, layer_slab=None, slab_xmin=-1, slab_offset=2, spiked=False, cross_section=cross_section).copy()

    return c

def grate_coupler_array(  gr: gf.Component, #grating coupler object
                        pitch: float = 127.0, # fiber array pitch 
                        n: int = 6, #number of grating couplers
                        loopback: bool = True, #include loopback for alignment
                        loopback_spacing = 20, #spacing between loopback and grating coupler
                        cross_section = "strip",
            ) -> gf.Component:
    
    c = gf.components.grating_coupler_array(grating_coupler=gr, pitch=pitch, n=n, port_name='o1', rotation=-90, with_loopback=loopback, cross_section=cross_section, straight_to_grating_spacing=loopback_spacing, centered=True, bend='bend_euler', mirror_grating_coupler=False).copy()
    return c