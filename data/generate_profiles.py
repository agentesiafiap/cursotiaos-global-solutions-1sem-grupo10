"""
Script para gerar dataset sintético de perfis de funcionários
Com controle de disparate impact para garantir equidade (≥ 0.8)
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

# Atributos protegidos para análise de disparate impact
GENEROS = ['Masculino', 'Feminino', 'Não-binário']
RACAS = ['Branca', 'Preta', 'Parda', 'Amarela', 'Indígena']
FAIXAS_ETARIAS = ['18-25', '26-35', '36-45', '46-55', '56+']

def generate_profile(profile_id):
    """Gera um perfil individual com atributos demográficos"""
    num_skills = random.randint(3, 5)
    num_interests = random.randint(2, 3)
    
    # Distribuição equilibrada de gênero
    genero_weights = [0.45, 0.45, 0.10]  # Masculino, Feminino, Não-binário
    genero = random.choices(GENEROS, weights=genero_weights)[0]
    
    # Distribuição baseada em dados demográficos brasileiros
    raca_weights = [0.43, 0.10, 0.45, 0.01, 0.01]  # Branca, Preta, Parda, Amarela, Indígena
    raca = random.choices(RACAS, weights=raca_weights)[0]
    
    # Distribuição de idade
    idade_weights = [0.15, 0.35, 0.30, 0.15, 0.05]
    faixa_etaria = random.choices(FAIXAS_ETARIAS, weights=idade_weights)[0]
    
    return {
        'id': profile_id,
        'nome': fake.name(),
        'genero': genero,
        'raca': raca,
        'faixa_etaria': faixa_etaria,
        'departamento': random.choice(DEPARTMENTS),
        'cargo': random.choice(POSITIONS),
        'habilidades': ', '.join(random.sample(SKILLS, num_skills)),
        'interesses': ', '.join(random.sample(INTERESTS, num_interests)),
        'disponivel_mentoria': random.choice([True, False])
    }

def calculate_disparate_impact(profiles, protected_attr, outcome_attr='disponivel_mentoria'):
    """
    Calcula disparate impact para um atributo protegido
    Retorna: {grupo: taxa_positiva} e menor_ratio
    """
    groups = {}
    for profile in profiles:
        group = profile[protected_attr]
        if group not in groups:
            groups[group] = {'total': 0, 'positive': 0}
        groups[group]['total'] += 1
        if profile[outcome_attr] in [True, 'True', 'true', '1', 1]:
            groups[group]['positive'] += 1
    
    # Calcular taxas
    rates = {group: data['positive'] / data['total'] if data['total'] > 0 else 0 
             for group, data in groups.items()}
    
    # Calcular disparate impact (menor taxa / maior taxa)
    if rates:
        max_rate = max(rates.values())
        min_rate = min(rates.values())
        di_ratio = min_rate / max_rate if max_rate > 0 else 0
    else:
        di_ratio = 0
    
    return rates, di_ratio, groups

def balance_mentorship(profiles):
    """
    Ajusta disponibilidade de mentoria para garantir DI ≥ 0.8
    para TODOS os atributos protegidos
    """
    # Taxa alvo de mentoria (60%)
    target_rate = 0.60
    
    # Balancear por cada atributo protegido
    for protected_attr in ['genero', 'raca', 'faixa_etaria']:
        # Agrupar perfis por atributo
        groups = {}
        for profile in profiles:
            group = profile[protected_attr]
            if group not in groups:
                groups[group] = []
            groups[group].append(profile)
        
        # Para cada grupo, garantir a taxa alvo
        for group, group_profiles in groups.items():
            target_count = max(1, int(len(group_profiles) * target_rate))  # Mínimo 1
            
            # Contar quantos já têm mentoria
            current_mentors = [p for p in group_profiles if p['disponivel_mentoria']]
            
            if len(current_mentors) < target_count:
                # Adicionar mais mentores
                non_mentors = [p for p in group_profiles if not p['disponivel_mentoria']]
                needed = target_count - len(current_mentors)
                to_add = random.sample(non_mentors, min(needed, len(non_mentors)))
                for p in to_add:
                    p['disponivel_mentoria'] = True
            elif len(current_mentors) > target_count:
                # Remover mentores excedentes
                excess = len(current_mentors) - target_count
                to_remove = random.sample(current_mentors, excess)
                for p in to_remove:
                    p['disponivel_mentoria'] = False
    
    return profiles

def main():
    """Gera o dataset completo com validação de disparate impact"""
    profiles = [generate_profile(i) for i in range(1, NUM_PROFILES + 1)]
    
    # Balancear mentoria para garantir equidade
    profiles = balance_mentorship(profiles)
    
    # Salvar em CSV
    with open('profiles.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'nome', 'genero', 'raca', 'faixa_etaria', 'departamento', 
                     'cargo', 'habilidades', 'interesses', 'disponivel_mentoria']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(profiles)
    
    print(f"✅ {NUM_PROFILES} perfis gerados com sucesso em 'profiles.csv'\n")
    
    # Estatísticas demográficas
    print("📊 Distribuição demográfica:")
    for attr in ['genero', 'raca', 'faixa_etaria', 'departamento']:
        counts = {}
        for p in profiles:
            val = p[attr]
            counts[val] = counts.get(val, 0) + 1
        print(f"\n{attr.capitalize()}:")
        for val, count in sorted(counts.items()):
            pct = (count / len(profiles)) * 100
            print(f"   - {val}: {count} ({pct:.1f}%)")
    
    # Análise de Disparate Impact
    print("\n" + "="*60)
    print("📈 ANÁLISE DE DISPARATE IMPACT (Disponível para Mentoria)")
    print("="*60)
    
    for attr in ['genero', 'raca', 'faixa_etaria']:
        rates, di_ratio, groups = calculate_disparate_impact(profiles, attr)
        print(f"\n{attr.upper()}:")
        for group, rate in sorted(rates.items()):
            count = groups[group]['positive']
            total = groups[group]['total']
            print(f"   - {group}: {rate:.1%} ({count}/{total})")
        
        status = "✅ APROVADO" if di_ratio >= 0.8 else "❌ REPROVADO"
        print(f"   Disparate Impact Ratio: {di_ratio:.3f} {status}")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
