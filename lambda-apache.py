import json
import boto3
import os

cf_client = boto3.client('cloudformation')

def lambda_handler(event, context):
    # Récupère le nom de la pile CloudFormation depuis les variables d'environnement, avec une valeur par défaut
    stack_name = os.environ.get('CLOUDFORMATION_STACK_NAME', 'MyALBDemoStack') 
    
    # Récupère l'URL S3 du modèle CloudFormation depuis les variables d'environnement
    # C'est la ligne corrigée cruciale : os.environ.get() prend le NOM de la variable
    template_url = os.environ.get('CLOUDFORMATION_TEMPLATE_URL') 

    # Si l'URL du template n'est pas trouvée (None ou chaîne vide), renvoie une erreur 400
    if not template_url:
        print("Erreur: CLOUDFORMATION_TEMPLATE_URL n'est pas défini ou est vide. Le template CloudFormation doit être sur S3.")
        return {
            'statusCode': 400,
            'body': json.dumps('Erreur: Le template CloudFormation doit être sur S3.')
        }

    # Récupère le nom de la paire de clés EC2 depuis les variables d'environnement, avec une valeur par défaut
    key_pair_name = os.environ.get('EC2_KEY_PAIR_NAME', 'wel-Paris') # Assurez-vous que 'wel-Paris' est bien votre paire de clés existante

    try:
        # Appelle l'API CloudFormation pour créer une nouvelle pile
        response = cf_client.create_stack(
            StackName=stack_name,
            TemplateURL=template_url, # Utilise l'URL du template S3
            Capabilities=['CAPABILITY_IAM'], # Nécessaire si le template crée des rôles ou politiques IAM
            Parameters=[ # Passe les paramètres définis dans le modèle CloudFormation
                {
                    'ParameterKey': 'KeyPairName',
                    'ParameterValue': key_pair_name
                }
            ]
        )
        print(f"Pile CloudFormation '{stack_name}' en cours de création. ID de la pile: {response['StackId']}")

        # Renvoie une réponse HTTP 200 en cas de succès
        return {
            'statusCode': 200,
            'body': json.dumps(f'Déploiement initié pour la pile {stack_name}. Vérifiez la console CloudFormation pour l\'état.')
        }
    except Exception as e:
        # Gère les erreurs lors de l'appel à CloudFormation ou pendant la création de la pile
        print(f"Erreur lors du déploiement de la pile CloudFormation: {e}")
        # Renvoie une réponse HTTP 500 en cas d'erreur
        return {
            'statusCode': 500,
            'body': json.dumps(f'Erreur lors du déploiement: {str(e)}. Vérifiez les logs Lambda et CloudWatch.')
        }
