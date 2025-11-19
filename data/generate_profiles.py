"""
Script para gerar dataset sintético de perfis de funcionários
Uso: python generate_profiles.py
"""

from faker import Faker
import csv
import random

fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)

# Configurações
NUM_PROFILES = 200
DEPARTMENTS = ['TI', 'RH', 'Vendas', 'Marketing']
POSITIONS = ['Júnior', 'Pleno', 'Sênior']
SKILLS = [
    'Python', 'JavaScript', 'SQL', 'Design', 'Excel', 
    'Liderança', 'Comunicação', 'Mentoria', 'Análise de Dados',
    'Marketing Digital', 'Gestão de Projetos', 'Inovação'
]
INTERESTS = [
    'Sustentabilidade', 'Inovação', 'Diversidade', 
    'Tecnologia', 'Educação', 'Saúde Mental'
]

def generate_profile(profile_id):
    """Gera um perfil individual"""
    num_skills = random.randint(3, 5)
    num_interests = random.randint(2, 3)
    
    return {
        'id': profile_id,
        'nome': fake.name(),
        'departamento': random.choice(DEPARTMENTS),
        'cargo': random.choice(POSITIONS),
        'habilidades': ', '.join(random.sample(SKILLS, num_skills)),
        'interesses': ', '.join(random.sample(INTERESTS, num_interests)),
        'disponivel_mentoria': random.choice([True, False])
    }

def main():
    """Gera o dataset completo"""
    profiles = [generate_profile(i) for i in range(1, NUM_PROFILES + 1)]
    
    # Salvar em CSV
    with open('profiles.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'nome', 'departamento', 'cargo', 'habilidades', 'interesses', 'disponivel_mentoria']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(profiles)
    
    print(f"✅ {NUM_PROFILES} perfis gerados com sucesso em 'profiles.csv'")
    print(f"📊 Distribuição por departamento:")
    
    dept_count = {}
    for profile in profiles:
        dept = profile['departamento']
        dept_count[dept] = dept_count.get(dept, 0) + 1
    
    for dept, count in sorted(dept_count.items()):
        print(f"   - {dept}: {count}")

if __name__ == '__main__':
    main()
