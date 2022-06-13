from doctest import FAIL_FAST
from email.encoders import encode_7or8bit
from random import randint
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

import markdown
from . import util
class SearchForm(forms.Form):
    q = forms.CharField(label='',
     widget= forms.TextInput(attrs={'placeholder':'Search Encyclopedia',
    'class':'q','autocomplete':'off'}))
class CreateNewPage(forms.Form):
    title = forms.CharField(label='',
        widget= forms.TextInput(attrs={'placeholder':'Enter title','class ':'title','autocomplete':'off','autofocus':True}))
    content = forms.CharField(label='',
        widget= forms.Textarea(attrs={'placeholder':'Enter the content',
         'class ':'content','autocomplete':'off'}))
class EditPage(forms.Form):
    # Making the title field uneditable 
    title = forms.CharField(label='',required=False,disabled=True,
        widget= forms.TextInput(attrs={'placeholder':'','class':'title'}))
    content = forms.CharField(label='',
        widget= forms.Textarea(attrs={'placeholder':'',
        'style':'width:1000px; height:400px; overflow-y: off','autocomplete':'off'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
        ,"form": SearchForm()
    })
def entry(request, title):
    # Checking if the desired title is in the encyclopedia
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "form": SearchForm()
            ,"exist": False
         
        })
    else:
        # Taking the information formated as Markdown code
        mdInfo = util.get_entry(title)
        # Convertion Markdown text into an html text
        info = markdown.markdown(mdInfo)
        # Showing the search result
   
        return render(request, "encyclopedia/entry.html", {
            "info": info,
            "form": SearchForm()
           , "title":title
        })
def search(request):
    if request.method == "GET":
        # The submited value
        form = request.GET['q']
        # A list of all entries
        all_entries = util.list_entries()
        found_entries = []
        
            # search for all the listed entries
        for entry in all_entries:
                if form.lower() == entry.lower():
                    return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'title':form}))
                # appending the list the entries
                elif form.lower() in entry.lower():
                    found_entries.append(entry)
        if not found_entries:
            # If search not found showing an error page
            return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'title':form}))
    # Rendring result page with a list of all antries that has
    # the querey as substring       
    return render(request,"encyclopedia/search.html",{
        "result": form,
        "entries": found_entries,
        "form": SearchForm()
    })

def new(request):
    if request.method == "POST":

        title = request.POST["title"]
        content = request.POST["content"]
        exist = False
        all_entries = util.list_entries()
        for entry in all_entries:
            # Checking if the new page is already in our entries
            if title.lower() == entry.lower():
                exist = True
                # if the page is found there will an error message that will be
                # shown to the user
                return render(request, "encyclopedia/new_page.html", {
                            "new": CreateNewPage(),
                            "form": SearchForm()
                            ,"exist": exist,
                            "title": title
                        })
        # If the new entry didn't exist 
        # then save it and redirect the user to the new page he created
        if not exist:
            util.save_entry(title,content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'title':title}))

                
    return render(request,"encyclopedia/new_page.html",{
        "form": SearchForm(),
        "new": CreateNewPage()
        ,"exist": False
    })
def random(request):
    if request.method=="GET":
        all_entries = util.list_entries()
        # Creating a radnom index for the user to shown a random entry 
        index = randint(0,len(all_entries)-1)
        entry = all_entries[index]
        return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'title':entry}))
def edit(request,title):
   if request.method =="GET":
       # At first we render the editing form with the pre existing informataton in the textarea
        info = util.get_entry(title)
        form = EditPage(initial={"title":title,"content":info})

        return render(request,"encyclopedia/edit.html",{
            "form":SearchForm(),
            "new":form,
            "info":info
            ,"title":title
        })
    # When the user submit the form update the information and redirect the user 
    # To the updated page
   if request.method == "POST":
        updatedInfo = request.POST['content']
        util.save_entry(title,updatedInfo)
        return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'title':title}))    

