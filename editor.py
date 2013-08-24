import swi
from pytag import T
import csv
import os
import random
import sys


def remove_non_ascii(text):
    return ''.join(x for x in text if ord(x)<128)
def parse_file(filename):
    with open(filename) as csvfile:
        data=[]
        
        for row in csv.reader(csvfile):
            d=[]
            for item in row:
                try:
                    item=item.decode('utf-8')
                except:
                    item=repr(item)
                d.append(item)
            data.append(d)
    return data
 
def quote(text):
    if '"' in text or ',' in text:
        return '"%s"'%text
    else:
        return text



class VoterType:
    def __init__(self,data):
        assert data[0][0]=='#'
        self.objectname=data[1]
        self.guiname=data[2]
        self.plural=data[3]
        self.image=data[4]
        self.overridden_joins=data[5]=='1'
        self.default = float(data[6])
        self.percentage = float(data[7])
        self.opposite = data[8]
        self.desc = data[9]
        assert data[10][0]=='#'
        self.influences = data[11:]
    
    def make_line(self):
        line=['#',
              self.objectname,
              self.guiname,
              self.plural,
              self.image,
              ['0', '1'][self.overridden_joins],
              '%g'%self.default,
              '%g'%self.percentage,
              self.opposite,
              self.desc,
              '#',
              ]
        line.extend(self.influences)
        line=[quote(item) for item in line]
        return ','.join(line)
        
    def save(self, filename, index):
        data=list(open(filename).readlines())
        data=[remove_non_ascii(row.strip()) for row in data]
        if index==-1:
            if len([d for d in data if len(d[0])>0 and d[0][0]=='#'])>=24:
                raise Exception('Maximum number of voter types (24) reached')
            data.append(self.make_line())
            index=len(data)-1
        else:    
            data[index]=self.make_line()
        open(filename,'w').write('\n'.join(data))
        return index

        
class Policy:
    def __init__(self,data):
        assert data[0][0]=='#'
        self.objectname=data[1]
        self.guiname=data[2]
        self.slider=data[3]
        self.description=data[4]
        self.flags=data[5]        
        self.actionpoints=[int(x) for x in data[6:10]]
        self.department=data[10]
        self.mincost=int(data[11])
        self.maxcost=int(data[12])
        self.cost_multiplier=data[13]
        self.implementation=int(data[14])
        self.minincome=float(data[15])
        self.maxincome=float(data[16])
        self.incomemultiplier=data[17]
        assert data[18][0]=='#'
        self.effects=data[19:]
    
    def make_line(self):
        line=['#',
              self.objectname,
              self.guiname,
              self.slider,
              self.description,
              self.flags,
              "%d"%self.actionpoints[0],
              "%d"%self.actionpoints[1],
              "%d"%self.actionpoints[2],
              "%d"%self.actionpoints[3],
              self.department,
              "%d"%self.mincost,
              "%d"%self.maxcost,
              self.cost_multiplier,
              "%d"%self.implementation,
              "%g"%self.minincome,
              "%g"%self.maxincome,
              self.incomemultiplier,
              '#Effects']
        line.extend(self.effects)
        line=[quote(item) for item in line]
        return ','.join(line)
        
    def save(self, filename, index):
        data=list(open(filename).readlines())
        data=[remove_non_ascii(row.strip()) for row in data]
        if index==-1:
            data.append(self.make_line())
            index=len(data)-1
        else:    
            data[index]=self.make_line()
        open(filename,'w').write('\n'.join(data))
        return index




class Variable:
    def __init__(self,data):
        assert data[0][0]=='#'
        self.name=data[1]
        self.guiname=data[2]
        self.description=data[3]
        self.zone = data[4]

        self.default = float(data[5])
        self.min = float(data[6])
        self.max = float(data[7])

        self.ishighgood = data[8]=='1'
        self.icon = data[9]
        assert data[10][0]=='#'
        assert data[11][0]=='#'
        
        self.effects=data[12:]
    
    def make_line(self):
        line=['#',
              self.name,
              self.guiname,
              self.description,
              self.zone,
              "%g"%self.default,
              "%g"%self.min,
              "%g"%self.max,

              ['0', '1'][self.ishighgood],
              self.icon,
              '#',
              '#',
              ]
        line.extend(self.effects)
        line=[quote(item) for item in line]
        return ','.join(line)
        
    def save(self, filename, index):
        data=list(open(filename).readlines())
        data=[remove_non_ascii(row.strip()) for row in data]
        if index==-1:
            data.append(self.make_line())
            index=len(data)-1
        else:    
            data[index]=self.make_line()
        open(filename,'w').write('\n'.join(data))
        return index





class Editor(swi.SimpleWebInterface):
    def swi_test(self, name):
        return T.body[T.h1['Hello'], T.p['My name is %s'%name], T.a(href='http://google.ca')['here is a link'], T.askjdhasdkja]
    


    def swi(self):
        return T.form(action='index', method='post')[
            'Name:',T.input(type='text',name='path', value='', size=40),
            ]
            
    def swi_index(self, path):       
        path=path.replace(' ','')
        path=path.replace('/','')
        path=path.replace('\\','')
        assert path!='simulation'
        assert len(path)>0
    
        # make a copy of the directory if a new person has logged in 
        if not os.path.isfile(path+'/simulation/Policies.csv'):
            os.system('mkdir %s'%path)
            if sys.platform.startswith('win32'):
                os.system(r'xcopy simulation "%s\simulation\" /e'%path) 
            else:    
                os.system('cp -R simulation %s/simulation'%path)
    
    
        # make the data for the four columns
        data=parse_file(path+'/simulation/Policies.csv')
        list=T.tbody(style='display:block; height:500px; overflow:auto; width:100%')
        for i,row in enumerate(data):
            bg=['#fff','#eee'][i%2]
            if row[0]=='#':
                list[T.tr(style='background:'+bg)[T.td[[T.a(href='/policy/%s/%d'%(path,i))[row[2]]]]]]
        policies=list

        data=parse_file(path+'/simulation/VoterTypes.csv')
        list=T.tbody(style='display:block; height:500px; overflow:auto; width:100%')
        for i,row in enumerate(data):
            bg=['#fff','#eee'][i%2]
            if row[0]=='#':
                list[T.tr(style='background:'+bg)[T.td[[T.a(href='/votertype/%s/%d'%(path,i))[row[2]]]]]]
        voters=list

        data=parse_file(path+'/simulation/simulation.csv')
        list=T.tbody(style='display:block; height:500px; overflow:auto; width:100%')
        for i,row in enumerate(data):
            bg=['#fff','#eee'][i%2]
            if row[0]=='#':
                list[T.tr(style='background:'+bg)[T.td[[T.a(href='/variable/%s/%d'%(path,i))[row[2]]]]]]
        variables=list
        
        events=T.tbody(style='display:block; height:500px; overflow:auto; width:100%')
        for i,file in enumerate(sorted([x for x in os.listdir(path+'/simulation/events') if x[0]!='_'])):
            bg=['#fff','#eee'][i%2]
            events[T.tr(style='background:'+bg)[T.td[[T.a(href='/event/%s/%s'%(path,file[:-4]))[file[:-4]]]]]]

        
        
        
        # make the actual page
        return T.body[
            T.table[T.tr[
                T.td[T.table(style='width:180px')[T.thead[T.tr[T.th['Policies']]],policies]],
                T.td[T.table(style='width:180px')[T.thead[T.tr[T.th['Voter Types']]],voters]],
                T.td[T.table(style='width:180px')[T.thead[T.tr[T.th['State Variables']]],variables]],
                T.td[T.table(style='width:180px')[T.thead[T.tr[T.th['Events']]],events]],
            ],
            T.tr[T.td[T.center[T.a(href="/raw/%s/policies"%path)['raw data']]],
                 T.td[T.center[T.a(href="/raw/%s/votertypes"%path)['raw data']]],
                 T.td[T.center[T.a(href="/raw/%s/variables"%path)['raw data']]], 
                 
                 ],
            T.tr[T.td[T.center[T.a(href="/toggle/%s/policies"%path)['toggle']]],
                 T.td[T.center[T.a(href="/toggle/%s/votertypes"%path)['toggle']]],
                 T.td[T.center[T.a(href="/toggle/%s/variables"%path)['toggle']]],
                ],
            ],
            T.td[T.center[T.a(href="/force/%s"%path)['force graph']]],
            ]
            
            
    
    def swi_csv(self):
        data=parse_file(path+'/simulation/Policies.csv')
        table=T.table()
        for row in data:
            tr=T.tr()
            for item in row:
                tr[T.td[item]]        
            table[tr]
        
        return table
        
    def swi_raw(self, path, type, text=None):
        fn=dict(policies='simulation/Policies.csv',
                votertypes='simulation/VoterTypes.csv',
                variables='simulation/simulation.csv')[type]
        if text is None:
            text=open(path+'/'+fn).read()
            text=text.replace('\x92', "'")
        else:
            file=open(path+'/'+fn,'w')
            file.write(text)
            file.close()
            
        form=T.form(action="/raw", method="post")[
            T.input(type="hidden", name="type", value=type),
            T.input(type="hidden", name="path", value=path),
            T.input(type="submit", value="Save Changes"),
            T.a(href="/index/"+path)['Back to main menu'],
            T.br,
            T.textarea(rows=50, cols=120, name='text')[text]
            ]
        return T.body[T.h1['Raw Data: '+fn],form]

    def swi_policies(self, path):
        data=parse_file(path+'/simulation/Policies.csv')
        list=T.ul
        for i,row in enumerate(data):
            if row[0]=='#':
                list[T.li[T.a(href='/policy/%s/%d'%(path,i))[row[2]]]]
        return T.body[T.h1['policies'],list]    

    def swi_toggle(self, path, type, **flags):
        fn=dict(policies='simulation/Policies.csv',
                votertypes='simulation/VoterTypes.csv',
                variables='simulation/simulation.csv')[type]
        data=open(path+'/'+fn).readlines()
        
        form=T.form(action="/toggle", method="post")[
                 T.input(type="hidden", name="type", value=type),
                 T.input(type="hidden", name="path", value=path),
                 T.a(href="/index/"+path)['Back to main menu'],
                 T.br,
                 T.input(type="submit", value="Save Changes"), 
                 T.br]
        for i,d in enumerate(data):
            if i==0: continue
            flag,id,name=d.split(',',3)[:3]
            if len(flags)>0:
                if 'id_'+id not in flags:
                    flag=''
                    if data[i].startswith('#'): data[i]=data[i][1:]
                else:
                    flag='#'
                    if not data[i].startswith('#'): data[i]='#'+data[i]
            
            if flag=='#':
                form[T.input(type='checkbox', id=id, name='id_'+id, value='Y', checked='checked')]
            else:         
                form[T.input(type='checkbox', id=id, name='id_'+id, value='Y')]
            form[T.label(**{'for':id})[name],T.br]
        form[T.input(type="submit", value="Save Changes")]
        
        if len(flags)>0:
            file=open(path+'/'+fn,'w')
            file.write(''.join(data))
            file.close()
            
        
        return T.body[T.h1[type],form]
        
    def swi_event(self, path, name, raw=None):
        fn = path+'/simulation/events/%s.txt'%name
        
        if raw is not None:
            f=open(fn, 'w')
            f.write(raw)
            f.close()
            
        
        data=open(fn).read()
    
        return T.body[
            T.h1[name],
            T.a(href="/index/"+path)['Back to menu'],

            T.br,
            T.div(style='background:#dddddd')[
                T.h3['Raw data:'],
                
                T.form(action='/event/%s/%s'%(path,name), method='post')[
                    T.textarea(rows=10, cols=60, name='raw')[data],
                    T.br,
                    T.input(type='submit', value='Save Raw Data'),
                    ],
                ],    


            ]
        

    
        
    def swi_policy(self, path, index, edit=False, guiname=None, description=None, 
                ap_intro=None, ap_cancel=None, ap_raise=None, ap_lower=None,
                effects=None, raw=None, duplicate=False, minincome=None,
                maxincome=None, mincost=None, maxcost=None, department=None,
                implementation=None):
        index=int(index)
        
        if raw!=None:
            data=csv.reader([raw]).next()
        else:
            data=parse_file(path+'/simulation/Policies.csv')[index]
 
        

 
        p=Policy(data)
        if raw!=None:
            p.save(path+'/simulation/Policies.csv',index)

        if edit:
            if guiname is not None: p.guiname=guiname
            if description is not None: p.description=description
            p.actionpoints=[int(ap_intro), int(ap_cancel), int(ap_raise), int(ap_lower)]
            p.effects=[item.strip() for item in effects.split('\n')]
            p.mincost=int(mincost)
            p.maxcost=int(maxcost)
            p.minincome=float(minincome)
            p.maxincome=float(maxincome)
            p.department=department
            p.implementation=int(implementation)
            
            p.save(path+'/simulation/Policies.csv',index)
            
        else:
            test=open(path+'/simulation/Policies.csv').readlines()[index].strip()
            if p.make_line()!=test:
                print 'file:',index,test
                print 'generated:',p.make_line()
        
        if duplicate:
            p.guiname+=' (copy)'
            p.objectname+='Copy'
            index=p.save(path+'/simulation/Policies.csv', -1)
            
        
        
        select=[{},dict(selected='selected')]
        
        return T.body[
            T.h1[p.objectname],
            T.a(href="/index/"+path)['Back to menu'],
            T.br,
            T.form(action="/policy/%s/%d"%(path,index), method='post') [
                T.input(type='hidden', name='duplicate', value=True),
                T.input(type='submit', value='Duplicate'),
              ],
            T.a(href="/policyvis/%s/%d"%(path, index))['visualize'],
            T.form(action='/policy/%s/%d'%(path,index), method='post')[
                T.input(type='hidden', name='edit', value=True),
                'Name:',T.input(type='text',name='guiname', value=p.guiname, size=40),
                T.br,
                T.textarea(rows=6, cols=60, name='description')[p.description],
                T.br,
                'Introduce:',
                      T.input(type='text',name='ap_intro',value=p.actionpoints[0], size=4),
                      'Cancel:',
                      T.input(type='text',name='ap_cancel',value=p.actionpoints[1], size=4),
                      'Raise:',
                      T.input(type='text',name='ap_raise',value=p.actionpoints[2], size=4),
                      'Lower:',
                      T.input(type='text',name='ap_lower',value=p.actionpoints[3], size=4),
                      
                T.br,
                'Department: ',
                T.select(name='department')[
                    T.option(value="FOREIGNPOLICY")(**select[p.department=='FOREIGNPOLICY'])['Foreign Policy'],
                    T.option(value="WELFARE")(**select[p.department=='WELFARE'])['Welfare'],
                    T.option(value="ECONOMY")(**select[p.department=='ECONOMY'])['Economy'],
                    T.option(value="TAX")(**select[p.department=='TAX'])['Tax'],
                    T.option(value="PUBLICSERVICES")(**select[p.department=='PUBLICSERVICES'])['Public Services'],
                    T.option(value="LAWANDORDER")(**select[p.department=='LAWANDORDER'])['Law and Order'],
                    T.option(value="TRANSPORT")(**select[p.department=='TRANSPORT'])['Transport'],
                    ],    
                T.br,
                'Cost: ',
                      T.input(type='text',name='mincost',value=p.mincost, size=8),
                      ' to ',
                      T.input(type='text',name='maxcost',value=p.maxcost, size=8),
                      ' (in $M per turn)',
                T.br,
                'Income: ',
                      T.input(type='text',name='minincome',value="%g"%p.minincome, size=8),
                      ' to ',
                      T.input(type='text',name='maxincome',value="%g"%p.maxincome, size=8),
                      ' (in $M per turn)',
                T.br,
                'Implementation Time:',
                      T.input(type='text',name='implementation',value=p.implementation, size=8),
                      ' (in months -- 4 months per turn)',
                T.br,
                'Effects:',
                T.br,                
                T.textarea(rows=6, cols=60, name='effects')['\n'.join(p.effects)],
                T.br,
                T.input(type='submit', value='Save Changes'),
                ],
            
            T.br,
            T.div(style='background:#dddddd')[
                T.h3['Raw data:'],
                
                T.form(action='/policy/%s/%d'%(path,index), method='post')[
                    T.textarea(rows=10, cols=60, name='raw')[p.make_line()],
                    T.br,
                    T.input(type='submit', value='Save Raw Data'),
                    ],
                ],    
            
            
            
            ]



    def swi_variable(self, path, index, edit=False, guiname=None, description=None, 
                zone=None, default=None, min=None, max=None, ishighgood=None, icon=None,
                effects=None, raw=None, duplicate=False):
        index=int(index)
        filename = path+'/simulation/simulation.csv'

        alldata = parse_file(filename)
        icons = []
        for data in alldata:
            if len(data[0])>0 and data[0][0]=='#':
                icon2 = Variable(data).icon
                if icon2 not in icons: icons.append(icon2)
        icons.sort()        
        
        if raw!=None:
            data=csv.reader([raw]).next()
        else:
            data=alldata[index]
 
        

 
        v=Variable(data)
        if raw!=None:
            v.save(filename,index)

        if edit:
            if guiname is not None: v.guiname=guiname
            if description is not None: v.description=description
            v.effects=[item.strip() for item in effects.split('\n')]
            v.zone = zone
            v.default = float(default)
            v.min = float(min)
            v.max = float(max)
            v.ishighgood = ishighgood=="1"
            v.icon = icon
            
            v.save(filename,index)
            
        else:
            test=open(filename).readlines()[index].strip()
            if v.make_line()!=test:
                print 'file:',index,test
                print 'generated:',p.make_line()
        
        if duplicate:
            v.guiname+=' (copy)'
            v.name+='Copy'
            index=v.save(filename, -1)
            
        
        
        select=[{},dict(selected='selected')]
        
        return T.body[
            T.h1[v.name],
            T.a(href="/index/"+path)['Back to menu'],
            T.br,
            T.form(action="/variable/%s/%d"%(path,index), method='post') [
                T.input(type='hidden', name='duplicate', value=True),
                T.input(type='submit', value='Duplicate'),
              ],
            T.form(action='/variable/%s/%d'%(path,index), method='post')[
                T.input(type='hidden', name='edit', value=True),
                'Name:',T.input(type='text',name='guiname', value=v.guiname, size=40),
                T.br,
                T.textarea(rows=6, cols=60, name='description')[v.description],
                T.br,
                      
                'Department: ',
                T.select(name='zone')[
                    T.option(value="FOREIGNPOLICY")(**select[v.zone=='FOREIGNPOLICY'])['Foreign Policy'],
                    T.option(value="WELFARE")(**select[v.zone=='WELFARE'])['Welfare'],
                    T.option(value="ECONOMY")(**select[v.zone=='ECONOMY'])['Economy'],
                    T.option(value="TAX")(**select[v.zone=='TAX'])['Tax'],
                    T.option(value="PUBLICSERVICES")(**select[v.zone=='PUBLICSERVICES'])['Public Services'],
                    T.option(value="LAWANDORDER")(**select[v.zone=='LAWANDORDER'])['Law and Order'],
                    T.option(value="TRANSPORT")(**select[v.zone=='TRANSPORT'])['Transport'],
                    ],    
                T.br,
                'Default value: ',
                      T.input(type='text',name='default',value="%g"%v.default, size=8),
                T.br,
                'Minimum: ',
                      T.input(type='text',name='min',value="%g"%v.min, size=8),
                      '  Maximum: ',
                      T.input(type='text',name='max',value="%g"%v.max, size=8),
  
                      T.select(name='ishighgood')[
                        T.option(value="1")(**select[v.ishighgood])['Larger is better'],
                        T.option(value="0")(**select[not v.ishighgood])['Smaller is better'],
                        ],    

                T.br,
                'Icon: ',
                T.select(name='icon')[[
                    T.option(value=icon)(**select[v.icon==icon])[icon] for icon in icons]],


                T.br,
                'Effects:',
                T.br,                
                T.textarea(rows=6, cols=60, name='effects')['\n'.join(v.effects)],
                T.br,
                T.input(type='submit', value='Save Changes'),
                ],
            
            T.br,
            T.div(style='background:#dddddd')[
                T.h3['Raw data:'],
                
                T.form(action='/variable/%s/%d'%(path,index), method='post')[
                    T.textarea(rows=10, cols=60, name='raw')[v.make_line()],
                    T.br,
                    T.input(type='submit', value='Save Raw Data'),
                    ],
                ],    
            
            
            
            ]






    def swi_votertype(self, path, index, edit=False, guiname=None, description=None, 
                percentage=None, effects=None, raw=None, duplicate=False):
        index=int(index)
        
        if raw!=None:
            data=csv.reader([raw]).next()
        else:
            data=parse_file(path+'/simulation/VoterTypes.csv')[index]
 
        

 
        vt=VoterType(data)
        if raw!=None:
            vt.save(path+'/simulation/VoterTypes.csv',index)

        if edit:
            if guiname is not None: vt.guiname=guiname
            if description is not None: vt.desc=description
            vt.percentage = min(1, max(float(percentage), 0))
            vt.influences=[item.strip() for item in effects.split('\n')]
            
            vt.save(path+'/simulation/VoterTypes.csv',index)
            
        else:
            test=open(path+'/simulation/VoterTypes.csv').readlines()[index].strip()
            if vt.make_line().strip()!=test:
                print 'error regenerating VoterType:'
                print 'file:',index
                print `test`
                print 'generated:'
                print `vt.make_line().strip()`
        
        if duplicate:
            vt.objectname+='Copy'
            vt.guiname+=' (copy)'
            index=vt.save(path+'/simulation/VoterTypes.csv', -1)
            
        
        
        select=[{},dict(selected='selected')]
        
        return T.body[
            T.h1[vt.objectname],
            T.a(href="/index/"+path)['Back to menu'],
            T.br,
            T.form(action="/votertype/%s/%d"%(path,index), method='post') [
                T.input(type='hidden', name='duplicate', value=True),
                T.input(type='submit', value='Duplicate'),
              ],
            T.form(action='/votertype/%s/%d'%(path,index), method='post')[
                T.input(type='hidden', name='edit', value=True),
                'Name:',T.input(type='text',name='guiname', value=vt.guiname, size=40),
                T.br,
                T.textarea(rows=6, cols=60, name='description')[vt.desc],
                T.br,
                'Proportion (0.0 to 1.0):',T.input(type='text',name='percentage', value=vt.percentage, size=10),
                T.br,
                'Influences:',
                T.br,                
                T.textarea(rows=6, cols=60, name='effects')['\n'.join(vt.influences)],
                T.br,
                T.input(type='submit', value='Save Changes'),
                ],
            
            T.br,
            T.div(style='background:#dddddd')[
                T.h3['Raw data:'],
                
                T.form(action='/votertype/%s/%d'%(path,index), method='post')[
                    T.textarea(rows=10, cols=60, name='raw')[vt.make_line()],
                    T.br,
                    T.input(type='submit', value='Save Raw Data'),
                    ],
                ],    
            
            
            
            ]





























            
    def swi_force(self, path):
        data=parse_file(path+'/simulation/simulation.csv')
        variables=[]
        variable_index={}
        for line in data:
            if line[0]=='#':
                v = Variable(line)
                variable_index[v.name] = len(variables)
                variables.append(v)
        
    
    
    
        html = open('force.html').read()
        
        
        
        
        nodes = []
        for i,variable in enumerate(variables):
            label = variable.name
            line = "node={label:'%s'}; nodes.push(node); labelAnchors.push({node:node}); labelAnchors.push({node:node});"%label
            line += "labelAnchorLinks.push({source: %d * 2, target : %d * 2 + 1, weight : 1});"%(i,i)
            nodes.append(line)
        nodes='\n'.join(nodes)    
        html=html.replace('/* ADD NODES HERE */', nodes)    

        links = []    
        for i,variable in enumerate(variables):
            for effect in variable.effects:
                if ',' in effect:
                    target, formula = effect.split(',',1)
                    if target in variable_index.keys():
                        j = variable_index[target]
                        line="links.push({source : %d, target : %d, weight : %f});"%(i,j,0.5)
                        links.append(line)
        links='\n'.join(links)    
        html=html.replace('/* ADD LINKS HERE */', links)    
                    
                    
            
            
        return html
    

    def swi_policyvis(self, path, index):
        policies = parse_file(path+'/simulation/Policies.csv')
        data = policies[int(index)]
        
        return data
    
    
        
		
		
    def swi_forcedata(self, path):
        data=[]
        depts = ['ECONOMY', 'TAX', 'FOREIGNPOLICY', 'PUBLICSERVICES', 'TRANSPORT', 'WELFARE', 'LAWANDORDER']
        
        for dept in depts:
            d = dict(Department=dept, PolicyName=dept, maxcost='100', mincost='0', URL='NONE')
            data.append(d)
        
        
        policies = parse_file(path+'/simulation/Policies.csv')
        
        for index,policy in enumerate(policies):
            if policy[0] == '#':
                p = Policy(policy)
                d = dict(Department=p.department, PolicyName=p.guiname, maxcost='%d'%p.maxcost, mincost=p.mincost, URL='/policy/%s/%d'%(path, index))
                data.append(d)
        
            
        import json        
        return json.dumps(dict(nodes=data))
        
    
        #return open('may24forcedata.json').read()

        

swi.start(Editor, 8080)
        
        
