import csv
import os


def generate_gv(filename, csvs):
    connections=[]

    for f in csvs:
        with open(f,'rU') as csvfile:
            for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
                if row[0]=='#':
                    name=row[1]
                    for val in row[::-1]:
                        if ',' in val:
                            name2,func=val.split(',')[:2]
                            connections.append((name,name2,func))
                        if val.startswith('#'):
                            break
                        
    lines=[]
    for c in connections:
            name,name2,func=c
            line='  %s -> %s [ label = "%s" ];'%(name, name2, func)
            lines.append(line)
    connection_text='\n'.join(lines)    


    gv="""
    digraph d2 {
        graph [ dpi = 450 ]; 
	    rankdir=LR;
	    size="8,5"
	    //node [shape = doublecircle]; LR_0 LR_3 LR_4 LR_8;
	    node [shape = circle];
	    %(connections)s
    }
    """%dict(connections=connection_text)

    open('%s.gv'%filename,'w').write(gv)

def generate_image(filename, type):
    os.system('dot -T%s %s.gv -o%s.%s'%(type,filename, filename,type))

if __name__ == '__main__':    
    generate_gv('simulation',['simulation/simulation.csv'])
    generate_gv('situations',['simulation/Situations.csv'])
    generate_gv('policies',['simulation/Policies.csv'])
    generate_gv('all',['simulation/simulation.csv','simulation/Situations.csv','simulation/Policies.csv'])



