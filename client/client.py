import requests
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading

# Настройка стиля (тёмный режим + неоновые акценты)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")  # Неоново-зелёный

class CryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("💎 CRYPTO DASHBOARD")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Кеш для данных (чтобы не грузить повторно)
        self.data_cache = {}
        
        # Список криптовалют (10 популярных)
        self.cryptos = [
            "bitcoin", "ethereum", "solana", "cardano", 
            "ripple", "dogecoin", "avalanche", "polkadot", 
            "shiba-inu", "toncoin"
        ]
        
        # Верхняя панель (стильная)
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=20, padx=20, fill="x")
        
        # Выбор криптовалюты
        self.crypto_dropdown = ctk.CTkComboBox(
            self.header,
            values=self.cryptos,
            font=("Roboto", 16),
            dropdown_font=("Roboto", 14),
            button_color="#4e9a06",
            border_color="#4e9a06",
            width=200,
            command=self.start_loading  # Запускаем загрузку при выборе
        )
        self.crypto_dropdown.pack(side="left", padx=10)
        
        # Кнопка обновления
        self.refresh_btn = ctk.CTkButton(
            self.header,
            text="🔄 ОБНОВИТЬ",
            font=("Roboto", 14, "bold"),
            fg_color="transparent",
            border_color="#4e9a06",
            border_width=2,
            hover_color="#4e9a06",
            command=self.start_loading
        )
        self.refresh_btn.pack(side="left")
        
        # Спиннер (прелоадер)
        self.spinner = ctk.CTkLabel(self.header, text="", width=20)
        self.spinner.pack(side="left", padx=10)
        
        # График (стиль Cyberpunk)
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(12, 7), facecolor="#0a0a0a")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
        
        # Статус-бар
        self.status = ctk.CTkLabel(
            self,
            text="▶ ВЫБЕРИТЕ КРИПТОВАЛЮТУ",
            font=("Roboto", 12),
            text_color="#4e9a06",
            corner_radius=10,
            fg_color="#1a1a1a",
            padx=10,
            pady=5
        )
        self.status.pack(pady=10)
    
    def start_loading(self, _=None):
        """Запускает загрузку в отдельном потоке (чтобы GUI не зависал)."""
        crypto = self.crypto_dropdown.get()
        self.status.configure(text=f"⌛ ЗАГРУЗКА {crypto.upper()}...")
        
        # Показываем спиннер
        self.spinner.configure(text="⏳")
        
        # Запускаем в потоке, чтобы не блокировать интерфейс
        thread = threading.Thread(target=self.update_graph, daemon=True)
        thread.start()
    
    def update_graph(self):
        """Основная функция обновления графика (без анимации)."""
        crypto = self.crypto_dropdown.get()
        
        # Если данные уже в кеше — берём оттуда
        if crypto in self.data_cache:
            self.draw_graph(self.data_cache[crypto], crypto)
            return
        
        try:
            # Запрос к API (может быть медленным)
            data = requests.get(f"http://127.0.0.1:8000/predict/{crypto}").json()
            
            if "error" in data:
                self.show_error(data["error"])
                return
            
            # Кешируем данные
            self.data_cache[crypto] = data
            self.draw_graph(data, crypto)
        
        except Exception as e:
            self.show_error(str(e))
    
    def draw_graph(self, data, crypto):
        """Рисует чёткий график без лишних элементов."""
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in data["dates"]]
        prices = data["prices"]
        preds = data["predictions"]
    
        # Очищаем график
        self.ax.clear()
    
        # --- Основные линии ---
        # Фактическая цена (сплошная линия)
        self.ax.plot(
            dates, 
            prices, 
            label="Цена", 
            color="#2ecc71",  # Зелёный
            linewidth=2,      # Умеренная толщина
            marker="",        # Убираем маркеры
            solid_capstyle="round",  # Закруглённые концы
        )
    
        # Прогноз (пунктир)
        self.ax.plot(
            dates, 
            preds, 
            label="Прогноз", 
            color="#e74c3c",  # Красный
            linestyle="--", 
            linewidth=1.5,
            marker="",        # Убираем маркеры
        )
    
        # --- Настройка осей ---
        self.ax.set_title(
            f"{crypto.upper()}: Цена и прогноз", 
            fontsize=14, 
            pad=10,
            color="white"
        )
    
        self.ax.set_xlabel("Дата", color="#aaaaaa")
        self.ax.set_ylabel("Цена (USD)", color="#aaaaaa")
    
        # Сетка (лёгкая)
        self.ax.grid(
            color="#333333", 
            linestyle="--", 
            linewidth=0.5,
            alpha=0.5
        )
    
        # Легенда (простая)
        self.ax.legend(
            facecolor="#1a1a1a",
            fontsize=10,
            framealpha=0.7
        )
    
        # Фон
        self.ax.set_facecolor("#0a0a0a")
        self.fig.set_facecolor("#0a0a0a")
    
        # Автоповорот дат
        plt.xticks(rotation=45, ha="right")
    
        # Фиксим отображение
        self.fig.tight_layout()
        self.canvas.draw()

    
    def show_error(self, error):
        """Показывает ошибку в статус-баре."""
        self.status.configure(text=f"❌ ОШИБКА: {error}", text_color="#ff5555")
        self.spinner.configure(text="")

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()