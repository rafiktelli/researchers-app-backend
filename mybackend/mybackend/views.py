from django.shortcuts import render
from django.http import JsonResponse
from .models import Teacher, Publication, FinalPublication
import json
from django.views.decorators.csrf import csrf_exempt
from .extract.main import extract_publications
from .extract.unifier import unify_publications
from .extract.interests import get_interests_scholar, get_interests_rgate

@csrf_exempt
def add_teacher(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        rg_interests = get_interests_rgate(data['email'], data['researchGate'])[0]['interests']
        gs_interests = get_interests_scholar(data['email'], data['googleScholar'])[0]['interests']
        print(rg_interests)
        
        teacher = Teacher(
            email=data['email'],
            full_name=data['fullName'],
            google_scholar=data['googleScholar'],
            research_gate=data['researchGate'],
            dblp=data['dblp'],
            rg_interests = '#'.join(rg_interests),
            gs_interests = '#'.join(gs_interests)
        )
        teacher.save()
        
        df1, df3 = extract_publications(data['email'], data['googleScholar'], data['researchGate'], data['dblp'])
        
        #create_publications(publications)
        print(df1)
        publications = unify_publications(df1, df1, df3)
        #print(publications)
        #print("the length of the unified publications is : ", len(publications))
        
        for _, row in publications.iterrows():
            my_instance = FinalPublication(
                source=row['source'],
                auth_id=row['auth_id'],
                title=row['title'],
                abstract=row['abstract'],
                authors=row['authors'],
                date=row['date'],
                journal=row['journal'],
                doi=row['doi'],
                norm_title=row['norm_title'],
                norm_abstract=row['norm_abstract'],
                order=row['order']
            )
            my_instance.save()
        
        
        
        
        return JsonResponse({'message': 'Teacher added successfully'})

    # Return a JSON response with a status code of 405 Method Not Allowed for other methods
    return JsonResponse({'message': 'Method Not Allowed'}, status=405)
    
def get_teacher_list(request):
    teachers = Teacher.objects.all().values() 
    print(teachers)
    return JsonResponse({'teachers': list(teachers)}, safe=False)


def get_teacher_by_email(request, email):
    try:
        teacher = Teacher.objects.filter(email=email).first()
        teacher_data = {
            'email': teacher.email,
            'full_name': teacher.full_name,
            'google_scholar': teacher.google_scholar,
            'research_gate': teacher.research_gate,
            'dblp': teacher.dblp,
        }
        return JsonResponse(teacher_data)
    except Teacher.DoesNotExist:
        return HttpResponseNotFound('Teacher not found')

def get_publications_by_email(request):
    email = request.GET.get('email')
    if email:
        publications = FinalPublication.objects.filter(auth_id=email)
        publications_data = [{
            'source': pub.source,
            'auth_id': pub.auth_id,
            'title': pub.title,
            'abstract': pub.abstract,
            'authors': pub.authors,
            'date': pub.date,
            'journal': pub.journal,
            'doi': pub.doi,
            'norm_title': pub.norm_title,
            'norm_abstract': pub.norm_abstract,
            'order': pub.order,
        } for pub in publications]
        return JsonResponse(publications_data, safe=False)
    else:
        return HttpResponseBadRequest('Invalid request')



    
def create_publications(publications):
    # Iterate through the list of dictionaries and create Publication instances
    for publication_data in publications:
        # Create a Publication instance for each dictionary
        publication = Publication(
            title=publication_data['title'],
            authors=', '.join(publication_data['authors']),  # Join author names into a single string
            date=publication_data['date'],
            journal_book=publication_data['journal/book'],
            doi=publication_data['doi'],
            auth_id=publication_data['auth_id'],
            lang=publication_data['lang'],
            abstract=publication_data['abstract'],
        )
        # Save the Publication instance to the database
        publication.save()