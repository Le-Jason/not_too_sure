import math as m
import numpy as np

def ECEF2LatLon(rECEF):
#Does not work yet
    R_Earth = 6378.1363
    e_Earth = 0.081819221456
    rdeltasat = m.sqrt((rECEF[0]**2) + (rECEF[1]**2))
    # alpha = m.asin(r[1]/rdeltasat)
    alpha = m.acos(rECEF[0]/rdeltasat)
    lon = alpha
    delta = m.atan(rECEF[2]/rdeltasat)
    lat_gd_old = delta
    rdelta = rdeltasat
    rk = rECEF[2]
    tol = 0.000001
    C_Earth = R_Earth / m.sqrt( 1 - ((e_Earth**2) * (m.sin(lat_gd_old)**2)) )
    tanlatgd = (rk + (C_Earth*(e_Earth**2)*m.sin(lat_gd_old)))/rdelta
    lat_gd = m.atan(tanlatgd)
    while ((lat_gd - lat_gd_old) > tol):
        lat_gd_old = lat_gd
        C_Earth = R_Earth / m.sqrt( 1 - ((e_Earth**2) * (m.sin(lat_gd_old)**2)) )
        tanlatgd = (rk + (C_Earth*(e_Earth**2)*m.sin(lat_gd_old)))/rdelta
        lat_gd = m.atan(tanlatgd)
    # if near poles (~1 deg) h_ellp = (rdelta/m.sin(lat_gd)) - S_Earth
    h_ellp = (rdelta/m.cos(lat_gd)) - C_Earth
    return lat_gd*180/m.pi, lon*180/m.pi, h_ellp

def ECEF2LatLonBorkowski(rECEF):
    R_Earth = 6378.1363
    b_Earth = 6356.7516005
    e_Earth = 0.081819221456
    rdeltasat = m.sqrt((rECEF[0]**2) + (rECEF[1]**2))
    a = R_Earth
    b = m.sqrt(b_Earth*(1 - (e_Earth**2)))*m.copysign(1,rECEF[2])
    E = ((b*rECEF[2]) - ((a**2) - (b**2))) / (a*rdeltasat)
    # alpha = m.asin(r[1]/rdeltasat)
    alpha = m.acos(rECEF[0]/rdeltasat)
    lon = alpha
    F = ((b*rECEF[2]) + ((a**2) - (b**2))) / (a*rdeltasat)
    P = (4*((E*F) + 1))/3
    Q = 2*((E**2) - (F**2))
    D = (P**3) + (Q**2)
    if (D >= 0):
        v = (m.sqrt(D) - Q)**(1./3.) - (m.sqrt(D) + Q)**(1./3.)
    elif (D < 0):
        v = 2*m.sqrt(-P)*m.cos((1/3)*m.acos(Q/(P*m.sqrt(-P))))
    G = (1/2)*(m.sqrt((E**2) + v) + E)
    t = m.sqrt((G**2) + ((F - (v*G))/((2*G) - E))) - G
    lat_gd = m.atan((a*(1 - (t**2)))/(2*b*t))
    h_ellp = ((rdeltasat - (a*t)) * m.cos(lat_gd)) + ((rECEF[2] - b)*m.sin(lat_gd))
    return lat_gd*180/m.pi,lon*180/m.pi,h_ellp


print(ECEF2LatLonBorkowski(np.array([6524.834,6862.875,6448.296])))