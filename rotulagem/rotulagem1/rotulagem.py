import tkinter as tk
import random

def mostra_palavra():
    
    if random.random() < 1/3:  # Probabilidade de 1/3 para exibir a palavra 
        label.config(text="APERTA", fg='red')
        # Definindo o tempo para esconder a palavra entre 500ms e 1200ms
        tempo = random.randint(500, 1500)
        root.after(tempo, esconde_palavra)  # Esconde a palavra após 0.5 segundos
    else:
        label.config(text=" ")  # Não mostra a palavra
        root.after(1000, mostra_palavra)  # Chama a função após 1 segundo

def esconde_palavra():
    label.config(text="")  # Esconde a palavra
    tempo = random.randint(1000, 1500)        
    root.after(tempo, mostra_palavra)  # Chama a função após 1 segundo

def main():
    # Criando a janela
    global root
    root = tk.Tk()
    root.title("Rotulagem")
    root.configure(bg='black')  # Definindo o fundo da janela como preto
    
    # tamanho da janela
    root.geometry("800x600")
    
    # Definindo as configurações de cor e fonte
    fonte = ("Helvetica", 90, "bold")
    
    # Criando um rótulo com o texto desejado
    global label
    label = tk.Label(root, text="", bg='black', fg='red', font=fonte)
    label.place(relx=0.5, rely=0.5, anchor='center')
    
    # Iniciando a função para mostrar a palavra
    root.after(0, mostra_palavra)
    
    # Iniciando o loop principal da janela
    root.mainloop()

if __name__ == "__main__":
    main()
