import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'rf_model.pkl')
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), 'encoders.pkl')

def train_initial_model():
    # Gerando dados fictícios para treinamento inicial do modelo
    np.random.seed(42)
    n_samples = 1000
    
    categorias = ['MANUTENÇÃO ELÉTRICA', 'MANUTENÇÃO HIDRÁULICA', 'MANUTENÇÃO ESTRUTURAL/CIVIL', 'CLIMATIZAÇÃO', 'SERVIÇOS GERAIS']
    prioridades = ['BAIXA', 'MÉDIA', 'ALTA']
    setores = ['RECEPÇÃO', 'RH', 'ADMINISTRAÇÃO', 'ALMOXARIFADO', 'SETOR DE TI', 'SANITÁRIO MASCULINO - TÉRREO']
    historico_tecnico = ['BOM', 'REGULAR', 'EXCELENTE', 'INICIANTE']
    
    dados = {
        'categoria': np.random.choice(categorias, n_samples),
        'prioridade': np.random.choice(prioridades, n_samples),
        'setor': np.random.choice(setores, n_samples),
        'historico_tecnico': np.random.choice(historico_tecnico, n_samples),
    }
    
    df = pd.DataFrame(dados)
    
    # Criando uma lógica de tempo (horas) baseada nas features
    tempos = []
    for index, row in df.iterrows():
        tempo = np.random.uniform(1.0, 4.0) # Base time
        if row['prioridade'] == 'ALTA': tempo += 1.0
        if row['prioridade'] == 'BAIXA': tempo += 4.0
        if row['categoria'] == 'MANUTENÇÃO ESTRUTURAL/CIVIL': tempo += 5.0
        if row['categoria'] == 'MANUTENÇÃO ELÉTRICA': tempo += 2.0
        if row['historico_tecnico'] == 'INICIANTE': tempo += 3.0
        if row['historico_tecnico'] == 'EXCELENTE': tempo -= 1.0
        tempos.append(max(0.5, tempo + np.random.normal(0, 0.5))) # Adding noise
        
    df['tempo_conclusao_horas'] = tempos
    
    # Encode categorical variables
    encoders = {}
    for col in ['categoria', 'prioridade', 'setor', 'historico_tecnico']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        
    X = df[['categoria', 'prioridade', 'setor', 'historico_tecnico']]
    y = df['tempo_conclusao_horas']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
        
    with open(ENCODERS_PATH, 'wb') as f:
        pickle.dump(encoders, f)
        
    print("Modelo e encoders treinados e salvos com sucesso.")

def predict_time(categoria, prioridade, setor, historico_tecnico='BOM'):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODERS_PATH):
        train_initial_model()
        
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(ENCODERS_PATH, 'rb') as f:
        encoders = pickle.load(f)
        
    def encode_val(le, val):
        if val in le.classes_:
            return le.transform([val])[0]
        else:
            return 0 # default or unknown fallback
            
    cat_encoded = encode_val(encoders['categoria'], categoria)
    prio_encoded = encode_val(encoders['prioridade'], prioridade)
    setor_encoded = encode_val(encoders['setor'], setor)
    hist_encoded = encode_val(encoders['historico_tecnico'], historico_tecnico)
    
    X_pred = np.array([[cat_encoded, prio_encoded, setor_encoded, hist_encoded]])
    prediction = model.predict(X_pred)[0]
    
    return round(prediction, 1)

if __name__ == '__main__':
    train_initial_model()
