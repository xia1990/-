#!/usr/bin/python
#_*_ coding:utf-8 _*_


import xlwt
import subprocess
import json
import re
import requests
import os

f1=open("change_list.txt","r")
flist=f1.readlines()
change_from_number_array=[]
total_line=len(flist)
commit_list=[]
gerrit_server="gerrit.mot.com"

def set_style(name,height,bold=False):
    style=xlwt.XFStyle()
    pattern=xlwt.Pattern()
    pattern.pattern=xlwt.Pattern.SOLID_PATTERN
    #设置背景颜色
    pattern.pattern_fore_colour=3
    style.pattern=pattern
    #设置边框(为实线)
    borders=xlwt.Borders()
    borders.left=xlwt.Borders.THIN
    borders.right=xlwt.Borders.THIN
    borders.top=xlwt.Borders.THIN
    borders.bottom=xlwt.Borders.THIN
    style.borders=borders
	
    font=xlwt.Font()
    font.bold=bold
    return style

def in_process():
	f=xlwt.Workbook(encoding="utf-8")
	sheet1=f.add_sheet("change_list",cell_overwrite_ok=True)
	row0=[u'Commit',u'cr',u'cr description',u'cr components',u'cr assign',u'repo path',u'commit message']

	for row in range(0,len(row0)):
		sheet1.write(0,row,row0[row],set_style('Times New Roman',400,True))

	for index,line in enumerate(flist):
		if line!="":
			if "changed from" in line:
				change_from_number_array.append(index)

	for change_index,change_number_index in enumerate(change_from_number_array):
		project_path=flist[change_number_index].split()[0]
		ssh1="repo list -n %s" % (project_path)
		process=subprocess.Popen(ssh1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		process.wait()
		project_name=process.stdout.read()

		#the last changed_from
		if change_index==len(change_from_number_array)-1:
			#print("the last changed from index:",change_number_index)
			commit_message=flist[change_number_index+1:total_line-1-1+1]
			if len(commit_message)==0:
				print("the changed from no commit")
			else:
				for commit_index,commit_line in enumerate(commit_message):
					commit_list.append(commit_line.split()[1])			
		else:
			commit_message=flist[change_number_index+1:change_from_number_array[change_index+1]-2+1]
			if len(commit_message)!=0:
				for commit_index,commit_line in enumerate(commit_message):
					commit_list.append(commit_line.split()[1])
			else:
				print("no commit!")

	for index,commit in enumerate(commit_list):
		print(commit)
		sheet1.write(index+1,0,commit)
		#cmd1="ssh -p 29418 %s gerrit query commit:%s --format JSON | egrep 'project|branch|subject'> temp.json" % (gerrit_server,commit)
		cmd1="ssh -p 29418 %s gerrit query commit:%s --format JSON | egrep 'project|branch|subject' | awk 'NR==1'" % (gerrit_server,commit)
		process=subprocess.Popen(cmd1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		process.wait()
		content=process.stdout.read()
		if content=="":
			if os.path.isdir(project_path):
				os.chdir(project_path)
				a1="git log %s -n 1 --format='%s'" % (commit,"%s")
				process=subprocess.Popen(a1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
				process.wait()
				subject=process.stdout.read()
				sheet1.write(index+1,6,subject)
				sheet1.write(index+1,5,project_name)
		else:
			message=json.loads(content)
			print(message)

			repo_path=message["project"]
			subject=message["subject"]
			sheet1.write(index+1,5,repo_path)
			sheet1.write(index+1,6,subject)

			cr=re.findall(r'IK[A-Z]*-[0-9]*',subject)
			if len(cr)==0:
				pass
			else:
				cr=cr=re.findall(r'IK[A-Z]*-[0-9]*',subject)[0]
				cr_url="https://idart.mot.com/browse/%s" % (cr)
				url="http://idart.mot.com/rest/api/2/issue/%s" % (cr)
				username="gaoyx9"
				password="gyx050400??"
				response=requests.get(url,auth=(username,password)).json()
				cr_description=response["fields"]["summary"]
				cr_component=response["fields"]["components"][0]["name"]
				cr_assign=response["fields"]["assignee"]["displayName"]
				sheet1.write(index+1,1,cr)
				sheet1.write(index+1,2,cr_description)
				sheet1.write(index+1,3,cr_component)
				sheet1.write(index+1,4,cr_assign)
				sheet1.write(index+1,5,repo_path)
				sheet1.write(index+1,6,subject)
			
		f.save("change_list.xls")

#==============================================
if __name__=="__main__":
	in_process()
