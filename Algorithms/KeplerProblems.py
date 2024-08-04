import math as m
import numpy as np

def c2c3(psi):
    if psi > 0.000001:
        c2 = (1 - m.cos(m.sqrt(psi)))/psi
        c3 = (m.sqrt(psi) - m.sin(m.sqrt(psi)))/(m.sqrt(psi**3))
    else:
        if (psi < -0.000001):
            c2 = (1 - m.cosh(m.sqrt(-psi)))/psi
            c3 = (m.sinh(m.sqrt(-psi)) - m.sqrt(-psi))/(m.sqrt((-psi)**3))
        else:
            c2 = 1/2
            c3 = 1/6
    return (c2,c3)

def KepEqtnE(M,e):
    tol = 0.00000001
    if (M > m.pi) or ((-m.pi < M) and (M < 0)):
        En = M - e
    else:
        En = M + e
    E = En + (M - En + (e*m.sin(En)))/(1 - (e*m.cos(En)))
    while (abs(E - En) > tol):
        En = E
        E = En + (M - En + (e*m.sin(En)))/(1 - (e*m.cos(En)))
    return E

def cot(x):
    return 1 / m.tan(x)

def arccot(x):
    return (m.pi / 2) - m.atan(x)

def KepEqtnP(deltat,p):
    mu = 398600.4418
    np = 2 * m.sqrt(mu/(p**3))
    cot2s = (3/2)*np*deltat
    s = arccot(cot2s)/2
    tan3w = m.tan(s)
    w = m.atan(tan3w**(1./3.))
    B = 2*cot(2*w)
    return B

def KepEqtnH(M,e):
    tol = 0.00000001
    if (e < 1.6):
        if ((M > m.pi) or ((-m.pi < M) and (M < 0))):
            Hn = M - e
        else:
            Hn = M + e
    else:
        if ((e < 3.6) and (abs(M) > m.pi)):
            Hn = M - (m.copysign(1,M)*e)
        else:
            Hn = M / (e - 1)
    H = Hn + (M - (e*m.sinh(Hn)) + Hn)/((e*m.cosh(Hn)) - 1)
    while (abs(H - Hn) > tol):
        Hn = H
        H = Hn + (M - (e*m.sinh(Hn)) + Hn)/((e*m.cosh(Hn)) - 1)
    return H

def v2Anomaly(e,v):
    if (e < 1.0):
        # sinE = (m.sin(v)*m.sqrt(1 - (e**2)))/(1 + (e*m.cos(v)))
        cosE = (e + m.cos(v)) / (1 + (e*m.cos(v)))
        E = m.acos(cosE)
        return E
    elif ( e == 1.0):
        B = m.tan(v/2)
        return B
    elif (e > 1.0):
        # sinhH = (m.sin(v)*m.sqrt((e**2) - 1))/(1 + (e*m.cos(v)))
        coshH = (e + m.cos(v)) / (1 + (e*m.cos(v)))
        H = m.acosh(coshH)
        return H
    print("v2Anomaly : error")
    return 1

def Anomaly2v(e,E,p=0,r=0):
    if (e < 1.0):
        # sinv = (m.sin(E)*m.sqrt(1 - (e**2)))/(1 - (e*m.cos(v)))
        cosv = (m.cos(E) - e) / (1 - (e*m.cos(E)))
        v = m.acos(cosv)
        return v
    elif ( e == 1.0):
        # sinv = (p*E)/r
        cosv = (p - r)/r
        v = m.acos(cosv)
        return v
    elif (e > 1.0):
        # sinhH = (-m.sinh(E)*m.sqrt((e**2) - 1))/(1 - (e*m.cosh(H)))
        coshv = (m.cosh(E) - e) / (1 - (e*m.cosh(E)))
        v = m.cos(coshv)
        return v
    print("Anomaly2v : error")
    return 1

def RV2COE(r, v, mu):
    '''
    %--------------------------------------------------------------------------
    %
    %  rv2coe: Finds the classical orbital elements given the geocentric
    %          equatorial position and velocity vectors.
    %
    %  Inputs:         description                    range / units
    %    r           - ijk position vector            m
    %    v           - ijk velocity vector            m/s
    %
    %  Outputs:
    %    p           - semilatus rectum               m
    %    a           - semimajor axis                 m
    %    ecc         - eccentricity
    %    incl        - inclination                    0.0  to pi rad
    %    omega       - longitude of ascending node    0.0  to 2pi rad
    %    argp        - argument of perigee            0.0  to 2pi rad
    %    nu          - true anomaly                   0.0  to 2pi rad
    %    m           - mean anomaly                   0.0  to 2pi rad
    %    arglat      - argument of latitude      (ci) 0.0  to 2pi rad
    %    truelon     - true longitude            (ce) 0.0  to 2pi rad
    %    lonper      - longitude of periapsis    (ee) 0.0  to 2pi rad
    %
    %--------------------------------------------------------------------------
    '''
    small = 1e-10
    undefined = 999999.1e6

    rmag = np.linalg.norm(r)
    vmag = np.linalg.norm(v)
    
    # find h n and e vectors
    h = np.cross(r.flatten(),v.flatten())
    hmag = np.linalg.norm(h)
    if ( hmag > small):
        K = np.array([0,0,1])
        n = np.cross(K,h)
        nmag = np.linalg.norm(n)
        e = ((((vmag**2) - (mu/rmag))*r) - (np.dot(r.flatten(),v.flatten())*v)) / mu
        emag = np.linalg.norm(e)

        # find a e and semi-latus rectum
        l = ((vmag**2)/2) - (mu/rmag)
        if (emag != 1.0):
            a = -mu/(2*l)
            if emag < 1.0:
                p = a*(1 - (emag**2))
            else:
                p = a*((emag**2) - 1)
        else:
            p = (hmag**2)/mu
            a = 10000000000000000000000 #inf

        # find inclination
        i = np.arccos(h[2]/hmag)

        # determine type of orbit for later use
        # elliptical, parabolic, hyperbolic inclined
        typeorbit = 'ei'
        if (emag < small):
            # circular equatorial
            if  (i < small) | (abs(i - np.pi) < small):
                typeorbit = 'ce'
            else:
                # circular inclined
                typeorbit = 'ci'
        else:
            # elliptical, parabolic, hyperbolic equatorial
            if (i < small) or (abs(i - np.pi) < small):
                typeorbit = 'ee'
        
        # find longitude of ascending node
        if (nmag > small):
            temp = n[0] / nmag
            if (abs(temp) > 1.0):
                temp = np.sign(temp)
            RAAN = np.arccos(temp)
            if (n[1] < 0):
                RAAN = (2*m.pi) - RAAN
        else:
            RAAN = undefined

        # find argument of perigee
        if typeorbit == 'ei':
            w = m.acos(np.dot(n.flatten(),e.flatten())/(nmag*emag))
            if e[2] < 0.0:
                w = 2*np.pi - w
        else:
            w = undefined

        # find true anomaly at epoch
        if 'e' in typeorbit:
            temp = np.dot(e.flatten(),r.flatten())/(emag*rmag)
            if (abs(temp) > 1.0):
                temp = np.sign(temp)
            truev = np.arccos(temp)
            if (np.dot(r.flatten(),v.flatten()) < 0):
                truev = 2*np.pi - truev

        # find argument of latitude - circular inclined
        if typeorbit == 'ci':
            arglat = np.arccos(np.dot(n,r.flatten())/(nmag*rmag))
            if (r[2] < 0):
                arglat = 2*np.pi - arglat
            me = arglat
        else:
            arglat = undefined
        
        # find longitude of perigee - elliptical equatorial
        if (emag > small) and (typeorbit == 'ee'):
            temp = e[0] / emag
            if (abs(temp) > 1.0):
                temp = np.sign(temp)
            lonper = np.arccos(temp)
            if (e[1] < 0.0):
                lonper = 2*np.pi - lonper
            if (i > np.pi/2):
                lonper = 2*np.pi - lonper
        else:
            lonper = undefined
        
        # find true longitude - circular equatorial
        if (rmag > small) and (typeorbit == 'ce'):
            temp = r[0] / rmag
            if (abs(temp) > 1.0):
                temp = np.sign(temp)
            truelon = np.arccos(temp)
            if (r[1] < 0):
                truelon = 2*np.pi - truelon
            if (i > np.pi/2):
                truelon = 2*np.pi - truelon
            me = truelon
        else:
            truelon = undefined
    else:
        p = undefined
        a = undefined
        emag = undefined
        i = undefined
        RAAN = undefined
        w = undefined
        truev = undefined
        arglat = undefined
        truelon = undefined
        lonper = undefined
    return (p, a, emag, i , RAAN, w, truev, arglat, truelon, lonper)

def ROT1(alpha):
    A = np.array([1.0, 0.0, 0.0,
                    0.0, m.cos(alpha), m.sin(alpha),
                    0.0, -m.sin(alpha), m.cos(alpha)])
    A = A.reshape((3,3))
    return A

def ROT2(alpha):
    A = np.array([m.cos(alpha), 0.0, -m.sin(alpha),
                    0.0, 1.0, 0.0,
                    m.sin(alpha), 0.0, m.cos(alpha)])
    A = A.reshape((3,3))
    return A

def ROT3(alpha):
    A = np.array([m.cos(alpha), m.sin(alpha), 0.0,
                    -m.sin(alpha), m.cos(alpha), 0.0,
                    0.0, 0.0, 1.0])
    A = A.reshape((3,3))
    return A


def COE2RV(p, e, i, RAAN, w, v, arglat, truelon, lonper, mu):
    '''
    % ------------------------------------------------------------------------------
    %
    %                           function coe2rv
    %
    %  this function finds the position and velocity vectors in geocentric
    %    equatorial (ijk) system given the classical orbit elements.
    %
    %  author        : david vallado                  719-573-2600    9 jun 2002
    %
    %  revisions
    %    vallado     - add constant file use                         29 jun 2003
    %
    %  inputs          description                    range / units
    %    p           - semilatus rectum               km
    %    ecc         - eccentricity
    %    incl        - inclination                    0.0  to pi rad
    %    omega       - longitude of ascending node    0.0  to 2pi rad
    %    argp        - argument of perigee            0.0  to 2pi rad
    %    nu          - true anomaly                   0.0  to 2pi rad
    %    arglat      - argument of latitude      (ci) 0.0  to 2pi rad
    %    truelon     - true longitude            (ce) 0.0  to 2pi rad
    %    lonper      - longitude of periapsis    (ee) 0.0  to 2pi rad
    %
    %  outputs       :
    %    r           - ijk position vector            km
    %    v           - ijk velocity vector            km / s
    %
    %  locals        :
    %    temp        - temporary real*8 value
    %    rpqw        - pqw position vector            km
    %    vpqw        - pqw velocity vector            km / s
    %    sinnu       - sine of nu
    %    cosnu       - cosine of nu
    %    tempvec     - pqw velocity vector
    %
    %  coupling      :
    %    mag         - magnitude of a vector
    %    rot3        - rotation about the 3rd axis
    %    rot1        - rotation about the 1st axis
    %
    %  references    :
    %    vallado       2007, 126, alg 10, ex 2-5
    %
    % [r,v] = coe2rv ( p,ecc,incl,omega,argp,nu,arglat,truelon,lonper );
    % ------------------------------------------------------------------------------
    '''
    small = 1e-10
    if e < small:
        # circular equatorial 
        if i < small or abs(i - np.pi) < small:
            w = 0.0
            RAAN = 0.0
            v = truelon
        # circular inclined
        else:
            w = 0.0
            v = arglat
    else:
        # elliptical equatorial
        if i < small or abs(i - np.pi) < small:
            w = lonper
            RAAN = 0.0

    # form pqw position and velocity vectors
    cosnu = np.cos(v)
    sinnu = np.sin(v)
    temp = p / (1.0 + e * cosnu)
    rPQW = [temp * cosnu,
            temp * sinnu,
            0.0]
    if abs(p) < 0.0001:
        p = 0.0001
    vPQW = [-sinnu * np.sqrt(mu) / np.sqrt(p),
            (e + cosnu) * np.sqrt(mu) / np.sqrt(p),
            0.0]
    
    # 3-1-3 Rotation: ROT3(-RAAN) * ROT1(-i) * ROT3(-w)
    # perform transformation to ijk
    T_PQW_IJK = np.dot(ROT1(-i), ROT3(-w))
    T_PQW_IJK = np.dot(ROT3(-RAAN), T_PQW_IJK)

    rIJK = np.dot(T_PQW_IJK, rPQW)
    vIJK = np.dot(T_PQW_IJK, vPQW)

    return rIJK, vIJK

def KeplerCOE(r0,v0,deltat):
    [p,a,e,i,RAAN,w,truev] = RV2COE(r0,v0)
    mu = 398600.4418
    np = m.sqrt(mu/a**3)
    if (e != 0):
        E0 = v2Anomaly(e,truev)
    else:
        E0 = truev # E = u or E = lambdatrue
    if (e < 1.0):
        M0 = E0 - (e*m.sin(E0))
        M = M0 + (np*deltat)
        E = KepEqtnE(M,e)
    elif (e == 1.0):
        h = np.corss(r0,v0)
        hNorm = m.sqrt(np.dot(h,h))
        p = (hNorm**2) / mu
        M0 = E0 + (E0**3/3)
        E = KepEqtnP(deltat,p)
    elif (e > 1.0):
        M0 = (e*m.sinh(E0) - E0)
        M = M0 + (np*deltat)
        E = KepEqtnH(M,e)
    if (e == 0):
        cur_v = Anomaly2v(e,E,p,m.sqrt(np.dot(r0,r0)))
    elif (e != 0):
        cur_v = Anomaly2v(e,E)
    else:
        u = E
        lambdatrue = E
    [r,v] = COE2RV(a,e,i,RAAN,w,cur_v)
    return (r,v)

def Kepler(r0,v0,deltat):
    mu = 398600.4418
    v0Norm = m.sqrt(np.dot(v0,v0))
    r0Norm = m.sqrt(np.dot(r0,r0))
    l = ((v0Norm**2)/2) - (mu/r0Norm)
    alpha = (-(v0Norm**2)/mu) + (2/r0Norm)
    if (alpha > 0.000001):
        Xn = m.sqrt(mu) * deltat * alpha
    elif (alpha == 1.0):
        print("Kepler : Too close to converge")
        return 0
    elif (abs(alpha) < 0.000001):
        h = np.cross(r0,v0)
        hNorm = m.sqrt(np.dot(h,h))
        p = (hNorm**2) / mu
        n = 2 * m.sqrt(mu/(p**3))
        cot2s = (3/2)*n*deltat
        s = arccot(cot2s)/2
        tan3w = m.tan(s)
        w = m.atan(tan3w**(1./3.))
        Xn = m.sqrt(p)*2*cot(2*w)
    elif (alpha < -0.000001):
        a = 1/alpha
        top = -2*mu*alpha*deltat
        bot = np.dot(r0,v0) + (m.copysign(1,deltat)*m.sqrt(-mu*a)*(1 - (r0Norm*alpha)))
        Xn = m.copysign(1,deltat)*m.sqrt(-a)*np.log(top/bot)
    psi = (Xn**2) * alpha
    [c2,c3] = c2c3(psi)
    rtemp = ((Xn**2)*c2) + (np.dot(r0,v0)/m.sqrt(mu))*Xn*(1-(psi*c3)) + (r0Norm*(1 - (psi*c2)))
    X = Xn + ((m.sqrt(mu)*deltat) - ((Xn**3)*c3) - ((np.dot(r0,v0)/m.sqrt(mu))*(Xn**2)*c2) - (r0Norm * Xn * (1 - (psi*c3)))) / rtemp
    tol = 0.000001
    while (abs(X - Xn) > tol):
        Xn = X
        psi = (Xn**2) * alpha
        [c2,c3] = c2c3(psi)
        rtemp = ((Xn**2)*c2) + (np.dot(r0,v0)/m.sqrt(mu))*Xn*(1-(psi*c3)) + (r0Norm*(1 - (psi*c2)))
        X = Xn + ((m.sqrt(mu)*deltat) - ((Xn**3)*c3) - ((np.dot(r0,v0)/m.sqrt(mu))*(Xn**2)*c2) - (r0Norm * Xn * (1 - (psi*c3)))) / rtemp
    f = 1 - ((X**2)/r0Norm)*c2
    g = deltat - ((X**3)/m.sqrt(mu))*c3
    fdot = (m.sqrt(mu)/(rtemp*r0Norm))*X*((psi * c3) - 1)
    gdot = 1 - (((X**2)/rtemp)*c2)
    r = (f*r0) + (g*v0)
    v = (fdot*r0) + (gdot*v0)
    if (m.isclose(((f*gdot) - (fdot*g)), 1, abs_tol = 1e-8)):
        return r,v
    else:
        print("Kepler : fgdot - fdotg did not equal 1")
        return r,v
    
def findTOF(r0, r1, p, mu):
    small = 1e-10
    if abs(p) < 0.0001:
        p = 0.0001

    r0mag = np.linalg.norm(r0)
    r1mag = np.linalg.norm(r1)

    temp = (np.dot(r0,r1))/(r0mag * r1mag)
    if (abs(temp) > 1.0):
        temp = np.sign(temp)
    cosdeltav = temp
    deltav = np.arccos(cosdeltav)

    k = r0mag*r1mag*(1 - cosdeltav)
    l = r0mag + r1mag
    ml = r0mag*r1mag*(1 + cosdeltav)
    temp = ((((2*ml) - (l**2))*p*p) + (2*k*l*p) - (k**2))
    if temp < small:
        temp = small
    a = (ml*k*p)/temp
    f = 1 - ((r1mag/p)*(1 - cosdeltav))
    g = (r0mag * r1mag * m.sin(deltav))/(m.sqrt(mu*p))

    TOF = 0.0
    if (a > 0.0):
        temp = 1 - ((r0mag/a)*(1 - f))
        if (abs(temp) > 1.0):
            temp = np.sign(temp)
        cosdeltaE = temp
        deltaE = m.acos(cosdeltaE)
        TOF = g + (m.sqrt(a**3/mu)*(deltaE - m.sin(deltaE)))

    if (a > 100000000000000000000):
        c = m.sqrt((r0mag**2) + (r1mag**2) - (2*r0mag*r1mag*m.cos(deltav)))
        s = (r0mag + r1mag + c) / 2
        TOF = (2/3)*(np.sqrt(s**3/(2*mu)))*(1 - (((s-c)/s)**(3/2)))

    elif (a < 0.0):
        coshdeltaH = 1 + ((f - 1)*(r0mag/a))
        deltaH = m.acosh(coshdeltaH)
        TOF = g + ((m.sqrt(((abs(a))**3)/mu))*(m.sinh(deltaH) - deltaH))
    return TOF
