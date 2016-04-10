import svgwrite
from svgwrite import cm
"""
Contains all svgwrite dependent methods
"""

def make_diagram(sol, depth, filename, sidelength, height, input_dict):
    """
    method called to make the diagram - calls importsvgwrite from interactive
    to import svgwrite, calls all necessary follow on methods and sets
    important variables
    """
    #extract the total breakdown value for scaling purposes
    total = sol(input_dict.keys()[0])
    #depth of each breakdown level
    elementlength = (sidelength/depth)
    dwg = svgwrite.Drawing(filename, debug=True)
    dwgrecurse(input_dict, (2, 2), -1, sol, elementlength, height, total, depth, dwg)
    #save the drawing at the conlusion of the recursive call
    dwg.save()

    return dwg

def dwgrecurse(input_dict, initcoord, currentlevel, sol, elementlength, sheight, total, depth, dwg):
    """
    recursive function to divide widnow into seperate units to be drawn and
    calls the draw function
    """
    totalheight = 0
    currentlevel = currentlevel+1
    for key in sorted(input_dict):
        height = int(round((((sheight/total)*sol(key)))))
        currentcoord = (initcoord[0], initcoord[1]+totalheight)
        drawsegment(key, height, currentcoord, dwg, elementlength)
        totalheight = totalheight+height
        if isinstance(input_dict[key], dict):
            #compute new initcoord
            newinitcoord = (initcoord[0]+elementlength,
                            initcoord[1]+totalheight-height)
            #recurse again
            dwgrecurse(input_dict[key], newinitcoord,
                       currentlevel, sol, elementlength, sheight, total, depth, dwg)
        #make sure all lines end at the same place
        elif currentlevel != depth:
            boundarylines = dwg.add(dwg.g(id='boundarylines',
                                          stroke='black'))
            #top boudnary line
            boundarylines.add(dwg.line(start=(currentcoord[0]*cm, currentcoord[1]*cm),
                                       end=((currentcoord[0] +
                                             (depth-currentlevel)*elementlength)*cm,
                                            currentcoord[1]*cm)))
            #bottom boundary line
            boundarylines.add(dwg.line(start=((currentcoord[0]+elementlength)*cm,
                                              (currentcoord[1]+height)*cm),
                                       end=((currentcoord[0] +(depth-currentlevel)
                                             *elementlength)*cm, (currentcoord[1]+height)*cm)))

def drawsegment(input_name, height, initcoord, dwg, elementlength):
    """
    #function to draw each poriton of the diagram
    """
    lines = dwg.add(dwg.g(id='lines', stroke='black'))
    #draw the top horizontal line
    lines.add(dwg.line(start=(initcoord[0]*cm, initcoord[1]*cm),
                       end=((initcoord[0]+elementlength)*cm, initcoord[1]*cm)))
    #draw the bottom horizontaal line
    lines.add(dwg.line(start=(initcoord[0]*cm, (initcoord[1]+height)*cm),
                       end=((initcoord[0]+elementlength)*cm,
                            (initcoord[1]+height)*cm)))
    #draw the vertical line
    lines.add(dwg.line(start=((initcoord[0])*cm, initcoord[1]*cm),
                       end=(initcoord[0]*cm, (initcoord[1]+height)*cm)))
    #adding in the breakdown namee
    writing = dwg.add(dwg.g(id='writing', stroke='black'))
    writing.add(svgwrite.text.Text(input_name,
                                   insert=None, x=[(.5+initcoord[0])*cm],
                                   y=[(float(height)/2+initcoord[1]+.125)*cm],
                                   dx=None, dy=None, rotate=None))