from django.shortcuts import render
from django.http import JsonResponse
from .models import Teacher, Publication, FinalPublication
import json
from django.views.decorators.csrf import csrf_exempt
from .extract.main import extract_publications
from .extract.unifier import unify_publications
from .extract.interests import get_interests_scholar, get_interests_rgate
from .extract.create_profile.Generate_Profile import generate_profile
from .extract.create_profile.assign_pfe import get_top_sim, get_sim_profiles
from .extract.create_profile.get_interests_classes import get_teachers_interests_classes
from .extract.create_profile.merge import process_json_files

@csrf_exempt
def add_teacher(request):
    if request.method == 'POST':
        print("STARTING --------------------------")
        data = json.loads(request.body)
        rg_interests = ['','']
        #rg_interests = get_interests_rgate(data['email'], data['researchGate'])[0]['interests']
        try:
            gs_interests = get_interests_scholar(data['email'], data['googleScholar'])[0]['interests']
        except:
            print("no gs account!")
        print(rg_interests)
        
        df1, df2, df3 = extract_publications(data['email'], data['googleScholar'], data['researchGate'], data['dblp'])
        
        publications = unify_publications(df1, df2, df3)
        my_profile, my_pub_proba, list_coeff = generate_profile(data['email'], publications)
        
        a = get_teachers_interests_classes(data['email'], gs_interests, my_pub_proba)
        final_decision = process_json_files(data['email'], my_pub_proba, a)
        
        teacher = Teacher(
            email=data['email'],
            full_name=data['fullName'],
            google_scholar=data['googleScholar'],
            research_gate=data['researchGate'],
            dblp=data['dblp'],
            rg_interests = '#'.join(rg_interests),
            gs_interests = '#'.join(gs_interests),
            pubs_proba = json.dumps(final_decision)
        )
        teacher.save()
        
        
        for index, row in publications.iterrows():
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
                order=row['order'],
                proba=json.dumps(my_profile[index]),
                coeff=list_coeff[index]
            )
            my_instance.save()
        
        
        
        
        print("BEGIN -----------------------------------------")
        #print(my_profile)
        #print(a)
        print(final_decision)
        print("END--------------------------------------------")
        
        return JsonResponse({'message': 'Teacher added successfully'})

    # Return a JSON response with a status code of 405 Method Not Allowed for other methods
    return JsonResponse({'message': 'Method Not Allowed'}, status=405)
    
def get_teacher_list(request):
    teachers = Teacher.objects.all().values() 
    print(teachers)
    return JsonResponse({'teachers': list(teachers)}, safe=False)

@csrf_exempt
def get_teachers_vectors(request):
    concatenated_values = request.GET.get('concatenatedValues', '')
    print('Concatenated Values:', concatenated_values)
    teachers_data = Teacher.objects.all().values('email', 'pubs_proba')
    #print(teachers)

    result = {}
    for teacher in teachers_data:
        email = teacher['email']
        pubs_proba_str = teacher['pubs_proba']
        pubs_proba_dict = json.loads(pubs_proba_str)
        result[email] = pubs_proba_dict
    print(result)
    all_sim, sub_classes = get_top_sim(concatenated_values, result)
    print(all_sim)
    return JsonResponse({'result': all_sim, 'sub': sub_classes }, status=200)

@csrf_exempt
def get_profiles_sim(request):
    email = request.GET.get('email', '')
    print(email)
    try:
        teacher = Teacher.objects.get(email=email)
        proba = teacher.pubs_proba 
        teachers_data = Teacher.objects.all().values('email', 'pubs_proba')
        teachers_data = {teacher['email']: json.loads(teacher['pubs_proba']) for teacher in teachers_data}
        top_profiles = get_sim_profiles(proba, teachers_data)
        print("here are my top profiles: ", top_profiles)
        return JsonResponse({'top': top_profiles }, status=200)
    except Teacher.DoesNotExist:
        # Handle the case where the Teacher does not exist
        print(email)
        return JsonResponse({'error': 'Teacher not found'}, status=404)
        
def get_teacher_by_email(request, email):
    try:
        teacher = Teacher.objects.filter(email=email).first()
        teacher_data = {
            'email': teacher.email,
            'full_name': teacher.full_name,
            'google_scholar': teacher.google_scholar,
            'research_gate': teacher.research_gate,
            'dblp': teacher.dblp,
            'pubs_proba': teacher.pubs_proba,
            'gs_interests' : teacher.gs_interests,
            'rg_interests' : teacher.rg_interests,
            
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
            'proba': pub.proba,
            'coeff': pub.coeff
        } for pub in publications]
        return JsonResponse(publications_data, safe=False)
    else:
        return HttpResponseBadRequest('Invalid request')






#-------------------------------------------------------------------------
    
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