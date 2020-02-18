import graphene
from graphene_django.types import DjangoObjectType
from .models import user_info
import json
from django.http import HttpResponse

class user_infoType(DjangoObjectType):
    class Meta:
        model = user_info

class Query(object):
    get_user_info = graphene.Field(user_infoType, username=graphene.String())

    def resolve_get_user_info(self, info, username):
        return user_info.objects.get(username=username)


    get_all_user_info = graphene.List(user_infoType)

    def resolve_get_all_user_info(self, info, **kwargs):
        return user_info.objects.all()


class create_market_item(graphene.Mutation):
 
    username = graphene.String()
    firstname = graphene.String()
    lastname = graphene.String()
    phone_number = graphene.String()
    goal = graphene.String()
    email = graphene.String()
    
    class Arguments:
        username = graphene.String()
        firstname = graphene.String()
        lastname = graphene.String()
        phone_number = graphene.String()
        goal = graphene.String()
        email = graphene.String()
 
    def mutate(self, info, username, firstname, lastname, phone_number, goal, email):
        User_info = user_info(username=username, firstname=firstname, lastname=lastname, phone_number=phone_number, goal=goal, email=email)
        User_info.save()
 
        return create_market_item(
            username=User_info.username,
            firstname=User_info.firstname,
            lastname=User_info.lastname,
            phone_number=User_info.phone_number,
            goal=goal,
            email=email
        )

class Mutation(graphene.ObjectType):
    create_user = create_market_item.Field() 
