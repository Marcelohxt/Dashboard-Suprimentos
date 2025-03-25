# Módulo de tratamento de outliers

import numpy as np
import pandas as pd

# Classe para tratamento de outliers em um DataFrame
class TrataOutlier:

    # Construtor que recebe um DataFrame e o armazena na classe
    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    # Função para contar o número de outliers em cada coluna, baseado no IQR (Intervalo Interquartílico)
    def count_outliers(self, Q1, Q3, IQR, columns):
        cut_off = IQR * 1.5  # Calcula o limite para outliers (1.5 vezes o IQR)
        # Verifica se os valores estão fora do intervalo definido (abaixo de Q1 - cut_off ou acima de Q3 + cut_off)
        temp_df = (self.df[columns] < (Q1 - cut_off)) | (self.df[columns] > (Q3 + cut_off))
        # Retorna o número de outliers para cada coluna
        return [len(temp_df[temp_df[col] == True]) for col in temp_df]

    # Função para calcular a assimetria (skew) de uma coluna ou de todas as colunas
    def calc_skew(self, columns=None):
        if columns == None:
            columns = self.df.columns  # Se nenhuma coluna for especificada, usa todas
        # Retorna a assimetria de cada coluna especificada
        return [self.df[col].skew() for col in columns]

    # Função para calcular a porcentagem de outliers em relação ao total de elementos (150001)
    def percentage(self, list):
        return [str(round(((value/150001) * 100), 2)) + '%' for value in list]

    # Função para remover os outliers de determinadas colunas com base no IQR
    def remove_outliers(self, columns):
        for col in columns:
            Q1, Q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)  # Quantis
            IQR = Q3 - Q1  # Calcula o IQR
            cut_off = IQR * 1.5  # Limite para outliers
            lower, upper = Q1 - cut_off, Q3 + cut_off  # Definindo os limites inferior e superior
            # Remove as linhas com valores abaixo do limite inferior ou acima do limite superior
            self.df = self.df.drop(self.df[self.df[col] > upper].index)
            self.df = self.df.drop(self.df[self.df[col] < lower].index)

    # Função para substituir os outliers por seus limites superiores ou inferiores (fences)
    def replace_outliers_with_fences(self, columns):
        for col in columns:
            Q1, Q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            cut_off = IQR * 1.5
            lower, upper = Q1 - cut_off, Q3 + cut_off

            # Substitui os valores acima do limite superior pelo valor do limite superior
            self.df[col] = np.where(self.df[col] > upper, upper, self.df[col])
            # Substitui os valores abaixo do limite inferior pelo valor do limite inferior
            self.df[col] = np.where(self.df[col] < lower, lower, self.df[col])

    # Função para obter uma visão geral das colunas especificadas, com estatísticas e contagem de outliers
    def getOverview(self, columns) -> None:
        min = self.df[columns].min()  # Valor mínimo
        Q1 = self.df[columns].quantile(0.25)  # Primeiro quartil
        median = self.df[columns].quantile(0.5)  # Mediana (segundo quartil)
        Q3 = self.df[columns].quantile(0.75)  # Terceiro quartil
        max = self.df[columns].max()  # Valor máximo
        IQR = Q3 - Q1  # Intervalo interquartílico
        skew = self.calc_skew(columns)  # Calcula a assimetria
        outliers = self.count_outliers(Q1, Q3, IQR, columns)  # Conta os outliers
        cut_off = IQR * 1.5  # Limite para outliers
        lower, upper = Q1 - cut_off, Q3 + cut_off  # Definição dos limites superior e inferior

        # Define os nomes das colunas para a nova tabela de resumo
        new_columns = ['Nome de Coluna', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'IQR', 'Lower fence', 'Upper fence', 'Skew', 'Num_Outliers', 'Percent_Outliers']
        
        # Cria a lista de dados a serem usados no resumo
        data = zip([column for column in self.df[columns]], min, Q1, median, Q3, max, IQR, lower, upper, skew, outliers, self.percentage(outliers))

        # Cria o DataFrame com o resumo e organiza os dados
        new_df = pd.DataFrame(data = data, columns = new_columns)
        
        new_df.set_index('Nome de Coluna', inplace = True)  # Define a coluna 'Nome de Coluna' como índice
        return new_df.sort_values('Num_Outliers', ascending = False).transpose()  # Ordena pelo número de outliers e transpõe o DataFrame


