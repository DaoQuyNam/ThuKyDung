import telebot
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

class TelegramNotifier(): 
    def __init__(self, noti_config):
        """Initialize TelegramNotifier class

        Args:
            token (str): The telegram API token.
            chat_id (str): The chat ID you want the bot to send messages to.
        """

        #self.bot = telegram.Bot(token=token)
        self.token = noti_config['token']
        self.chat_id = noti_config['chat_id']
        
    @retry(
        retry=retry_if_exception_type(telebot.apihelper.ApiTelegramException),
        stop=stop_after_attempt(3),
        wait=wait_fixed(60)
    )

    def send(self, message):
        #elf.bot.send_message(chat_id=self.chat_id, text=message)
        tb = telebot.TeleBot(self.token)
        tb.send_message(self.chat_id, message)
        print('Message Sent!')
        