#!/usr/bin/env python3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram.error import TimedOut, NetworkError
import os
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
TOTAL_INHERITANCE, DEBTS, HAS_WILL, WILL_AMOUNT, IS_MURDERER, IS_DIFFERENT_FAITH, HAS_SPOUSE, HAS_WIFE, NUM_DAUGHTERS, NUM_SONS, NUM_GRANDDAUGHTERS, NUM_GRANDSONS, HAS_FATHER, HAS_MOTHER, HAS_GRANDFATHER, HAS_GRANDMOTHER, NUM_SIBLINGS_SISTERS, NUM_SIBLINGS_BROTHERS, NUM_COUSINS_SISTERS, NUM_COUSINS_BROTHERS = range(
    20)


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask for the total inheritance amount."""
    # Initialize user data
    context.user_data.clear()
    
    # Remove keyboard during calculation process
    update.message.reply_text(
        'Ассаламу алейкум! 🌙\n\n'
        '*КАЛЬКУЛЯТОР НАСЛЕДСТВА PRO* 📊\n\n'
        'Я помогу рассчитать доли наследства по исламским законам (фараиз) с учетом расширенных правил:\n'
        '• Завещание (васия)\n'
        '• Особые случаи (убийство, различие в вере)\n'
        '• Особое правило для сестер\n'
        '• Учет родственников всех категорий\n\n'
        'Введите общую сумму наследства (только число):',
        parse_mode='Markdown')
    
    return TOTAL_INHERITANCE


def handle_total_inheritance(update: Update, context: CallbackContext) -> int:
    """Parse and store the total inheritance amount."""
    try:
        total = float(update.message.text.replace(',', '.'))
        if total <= 0:
            raise ValueError("Сумма наследства должна быть положительной")

        context.user_data['total_inheritance'] = total
        update.message.reply_text(
            f'Сумма наследства: {total}\nВведите общую сумму долгов (если нет, введите 0):'
        )
        return DEBTS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите корректное число:')
        return TOTAL_INHERITANCE


def handle_debts(update: Update, context: CallbackContext) -> int:
    """Parse and store the debts amount."""
    try:
        debts = float(update.message.text.replace(',', '.'))
        if debts < 0:
            raise ValueError("Сумма долгов не может быть отрицательной")

        context.user_data['debts'] = debts
        update.message.reply_text(
            'Оставил ли наследодатель завещание? (введите 1 - да, 0 - нет)')
        return HAS_WILL
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите корректное число:')
        return DEBTS
        
        
def handle_has_will(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased left a will."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        has_will = bool(int(text))
        context.user_data['has_will'] = has_will
        
        if has_will:
            update.message.reply_text(
                'Какую сумму наследодатель указал в завещании? (до 1/3 от общей суммы наследства)')
            return WILL_AMOUNT
        else:
            update.message.reply_text(
                'Есть ли супруг (муж)? (введите 1 - да, 0 - нет)')
            return HAS_SPOUSE
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_WILL
        
        
def handle_will_amount(update: Update, context: CallbackContext) -> int:
    """Parse and store the amount specified in the will."""
    try:
        will_amount = float(update.message.text.replace(',', '.'))
        if will_amount < 0:
            raise ValueError("Сумма в завещании не может быть отрицательной")
            
        total_inheritance = float(context.user_data.get('total_inheritance', 0))
        debts = float(context.user_data.get('debts', 0))
        net_inheritance = max(0, total_inheritance - debts)
        
        max_will_amount = net_inheritance / 3  # Не более 1/3 от наследства по исламскому праву
        
        if will_amount > max_will_amount:
            update.message.reply_text(
                f'Предупреждение: По исламскому праву нельзя завещать более 1/3 от общего наследства. '
                f'Максимальная сумма завещания: {max_will_amount:.2f}. '
                f'Сумма будет ограничена до {max_will_amount:.2f}.')
            will_amount = max_will_amount
            
        context.user_data['will_amount'] = will_amount
        update.message.reply_text(
            'Есть ли среди наследников тот, кто лишил жизни наследодателя? (введите 1 - да, 0 - нет)')
        return IS_MURDERER
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите корректное число:')
        return WILL_AMOUNT
        
        
def handle_is_murderer(update: Update, context: CallbackContext) -> int:
    """Parse and store whether there is a heir who killed the deceased."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        is_murderer = bool(int(text))
        context.user_data['is_murderer'] = is_murderer
        
        update.message.reply_text(
            'Есть ли среди наследников немусульмане? (введите 1 - да, 0 - нет)')
        return IS_DIFFERENT_FAITH
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return IS_MURDERER
        
        
def handle_is_different_faith(update: Update, context: CallbackContext) -> int:
    """Parse and store whether there are heirs of different faith."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        is_different_faith = bool(int(text))
        context.user_data['is_different_faith'] = is_different_faith
        
        update.message.reply_text(
            'Есть ли супруг (муж)? (введите 1 - да, 0 - нет)')
        return HAS_SPOUSE
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return IS_DIFFERENT_FAITH


def handle_has_spouse(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased has a spouse (husband)."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        context.user_data['has_spouse'] = bool(int(text))
        update.message.reply_text(
            'Есть ли супруга (жена)? (введите 1 - да, 0 - нет)')
        return HAS_WIFE
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_SPOUSE


def handle_has_wife(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased has a wife."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        context.user_data['has_wife'] = bool(int(text))
        update.message.reply_text('Сколько дочерей? (введите число)')
        return NUM_DAUGHTERS
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_WIFE


def handle_num_daughters(update: Update, context: CallbackContext) -> int:
    """Parse and store the number of daughters."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_daughters'] = num
        update.message.reply_text('Сколько сыновей? (введите число)')
        return NUM_SONS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_DAUGHTERS


def handle_num_sons(update: Update, context: CallbackContext) -> int:
    """Parse and store the number of sons."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_sons'] = num
        update.message.reply_text('Сколько внучек? (введите число)')
        return NUM_GRANDDAUGHTERS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_SONS


def handle_num_granddaughters(update: Update, context: CallbackContext) -> int:
    """Parse and store the number of granddaughters."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_granddaughters'] = num
        update.message.reply_text('Сколько внуков? (введите число)')
        return NUM_GRANDSONS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_GRANDDAUGHTERS


def handle_num_grandsons(update: Update, context: CallbackContext) -> int:
    """Parse and store the number of grandsons."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_grandsons'] = num
        update.message.reply_text(
            'Жив ли отец наследодателя? (введите 1 - да, 0 - нет)')
        return HAS_FATHER
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_GRANDSONS


def handle_has_father(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased's father is alive."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        context.user_data['has_father'] = bool(int(text))
        update.message.reply_text(
            'Жива ли мать наследодателя? (введите 1 - да, 0 - нет)')
        return HAS_MOTHER
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_FATHER


def handle_has_mother(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased's mother is alive."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        context.user_data['has_mother'] = bool(int(text))
        update.message.reply_text(
            'Жив ли дедушка (по отцовской линии)? (введите 1 - да, 0 - нет)')
        return HAS_GRANDFATHER
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_MOTHER


def handle_has_grandfather(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased's grandfather is alive."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        context.user_data['has_grandfather'] = bool(int(text))
        update.message.reply_text(
            'Жива ли бабушка (по отцовской линии)? (введите 1 - да, 0 - нет)')
        return HAS_GRANDMOTHER
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_GRANDFATHER


def handle_has_grandmother(update: Update, context: CallbackContext) -> int:
    """Parse and store whether the deceased's grandmother is alive."""
    try:
        text = update.message.text.strip()
        if text not in ["0", "1"]:
            raise ValueError("Пожалуйста, введите 1 для 'да' или 0 для 'нет'")

        context.user_data['has_grandmother'] = bool(int(text))
        update.message.reply_text(
            'Сколько родных сестёр у наследодателя? (введите число)')
        return NUM_SIBLINGS_SISTERS
    except ValueError as e:
        update.message.reply_text(f'Ошибка: {str(e)}')
        return HAS_GRANDMOTHER


def handle_num_siblings_sisters(update: Update,
                              context: CallbackContext) -> int:
    """Parse and store the number of sisters."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_siblings_sisters'] = num
        update.message.reply_text(
            'Сколько родных братьев у наследодателя? (введите число)')
        return NUM_SIBLINGS_BROTHERS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_SIBLINGS_SISTERS


def handle_num_siblings_brothers(update: Update,
                               context: CallbackContext) -> int:
    """Parse and store the number of brothers."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_siblings_brothers'] = num
        update.message.reply_text(
            'Сколько двоюродных сестёр у наследодателя? (введите число)')
        return NUM_COUSINS_SISTERS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_SIBLINGS_BROTHERS


def handle_num_cousins_sisters(update: Update,
                               context: CallbackContext) -> int:
    """Parse and store the number of sisters."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_cousins_sisters'] = num
        update.message.reply_text(
            'Сколько двоюродных братьев у наследодателя? (введите число)')
        return NUM_COUSINS_BROTHERS
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_COUSINS_SISTERS


def handle_num_cousins_brothers(update: Update,
                                context: CallbackContext) -> int:
    """Parse and store the number of brothers and complete the calculation."""
    try:
        num = int(update.message.text.strip())
        if num < 0:
            raise ValueError("Число не может быть отрицательным")

        context.user_data['num_cousins_brothers'] = num

        # Calculate inheritance shares
        inheritance_data = calculate_inheritance(context.user_data)

        # Format the response
        response = format_inheritance_response(context.user_data, inheritance_data)

        # Создаем клавиатуру с кнопками для результата
        keyboard = [
            [KeyboardButton('🧮 Начать расчет')],
            [KeyboardButton('💰 Донат'), KeyboardButton('💬 Отзывы и предложения')]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        return ConversationHandler.END
    except ValueError as e:
        update.message.reply_text(
            f'Ошибка: {str(e)}. Пожалуйста, введите целое число:')
        return NUM_COUSINS_BROTHERS


def calculate_inheritance(user_data):
    """Calculate inheritance shares based on Islamic inheritance laws."""
    total_inheritance = float(user_data.get('total_inheritance', 0))
    debts = float(user_data.get('debts', 0))
    has_will = user_data.get('has_will', False)
    will_amount = float(user_data.get('will_amount', 0)) if has_will else 0
    is_murderer = user_data.get('is_murderer', False)  # Есть ли убийца среди наследников
    is_different_faith = user_data.get('is_different_faith', False)  # Есть ли наследники другой веры

    # Calculate net inheritance after debts
    net_inheritance = max(0, total_inheritance - debts)

    if net_inheritance <= 0:
        return {
            "amounts": {"Ошибка": "После выплаты долгов не осталось средств для распределения"},
            "fractions": {},
            "percentages": {},
            "explanations": {}
        }
    
    # Проверка суммы завещания (не более 1/3 наследства)
    max_will_amount = net_inheritance / 3
    will_amount = min(will_amount, max_will_amount)

    # Initialize shares for different family members
    amounts = {}  # Денежные суммы
    fractions = {}  # Доли в виде дробей
    percentages = {}  # Процентное соотношение
    explanations = {}  # Объяснения для наследников без доли
    
    # Предупреждения о специальных случаях
    if is_murderer:
        explanations["Предупреждение"] = "По исламскому праву убийца не может наследовать имущество своей жертвы. Согласно учению Мухаммеда ибн Идрис Шафии, убийца во всех случаях лишается права наследовать после своей жертвы (за исключением убийства в приступе безумия или совершенного малолетним). Есть и другие трактовки о сохранении права наследования в случаях убийства при самозащите или по несчастному случаю. Рекомендуем проконсультироваться с имамом или исламским юристом."
    
    if is_different_faith:
        explanations["Предупреждение о вере"] = "По исламскому праву немусульмане не могут наследовать от мусульман, а мусульмане не могут наследовать от немусульман. Это правило относится как к наследникам по родству, так и по завещанию. Рекомендуем проконсультироваться с имамом или исламским юристом."
    
    # Учитываем завещание, если оно есть
    if has_will and will_amount > 0:
        amounts["Завещание (васия)"] = will_amount
        will_percentage = (will_amount / net_inheritance) * 100
        percentages["Завещание (васия)"] = will_percentage
        fractions["Завещание (васия)"] = "≤1/3"
        explanations["О завещании (васия)"] = "Согласно исламскому праву, завещание (васия) может составлять не более 1/3 от всего наследства. Распределение по завещанию происходит после выплаты долгов умершего, но до распределения наследства между родственниками. Наследники по родству не могут одновременно быть наследниками по завещанию."
        # Уменьшаем оставшуюся сумму
        remaining = net_inheritance - will_amount
    else:
        remaining = net_inheritance

    # Islamic inheritance calculation rules
    # 1. First allocate fixed shares (Fard)
    # 2. Then distribute remaining to agnatic heirs (Asaba)

    # Spouse shares
    if user_data.get('has_spouse', False):
        has_descendants = (user_data.get('num_sons', 0) > 0
                           or user_data.get('num_daughters', 0) > 0
                           or user_data.get('num_grandsons', 0) > 0
                           or user_data.get('num_granddaughters', 0) > 0)

        if has_descendants:
            spouse_share = net_inheritance * 0.25
            fractions["Супруг (муж)"] = "1/4"
            percentages["Супруг (муж)"] = 25.0
            explanations["О доле мужа"] = "Согласно аяту 12 суры Ан-Ниса (Женщины): «Вам принадлежит половина того, что оставили ваши жены, если у них нет ребенка. Но если у них есть ребенок, то вам принадлежит четверть того, что они оставили»."
        else:
            spouse_share = net_inheritance * 0.5
            fractions["Супруг (муж)"] = "1/2"
            percentages["Супруг (муж)"] = 50.0
            explanations["О доле мужа"] = "Согласно аяту 12 суры Ан-Ниса (Женщины): «Вам принадлежит половина того, что оставили ваши жены, если у них нет ребенка»."
            
        amounts["Супруг (муж)"] = spouse_share
        remaining -= spouse_share

    if user_data.get('has_wife', False):
        has_descendants = (user_data.get('num_sons', 0) > 0
                           or user_data.get('num_daughters', 0) > 0
                           or user_data.get('num_grandsons', 0) > 0
                           or user_data.get('num_granddaughters', 0) > 0)

        if has_descendants:
            wife_share = net_inheritance * 0.125
            fractions["Супруга (жена)"] = "1/8"
            percentages["Супруга (жена)"] = 12.5
            explanations["О доле жены"] = "Согласно аяту 12 суры Ан-Ниса (Женщины): «Им принадлежит четверть того, что вы оставили, если у вас нет ребенка. Но если у вас есть ребенок, то им принадлежит одна восьмая того, что вы оставили»."
        else:
            wife_share = net_inheritance * 0.25
            fractions["Супруга (жена)"] = "1/4"
            percentages["Супруга (жена)"] = 25.0
            explanations["О доле жены"] = "Согласно аяту 12 суры Ан-Ниса (Женщины): «Им принадлежит четверть того, что вы оставили, если у вас нет ребенка»."
            
        amounts["Супруга (жена)"] = wife_share
        remaining -= wife_share

    # Parents shares
    if user_data.get('has_father', False):
        has_sons = user_data.get('num_sons', 0) > 0
        if has_sons:
            father_share = net_inheritance * (1/6)
            fractions["Отец"] = "1/6"
            percentages["Отец"] = 16.67
            explanations["О доле отца"] = "Согласно аяту 11 суры Ан-Ниса (Женщины): «Каждому из родителей принадлежит одна шестая того, что он оставил, если у него есть ребенок». Отец получает фиксированную долю 1/6 наследства."
        else:
            father_share = remaining  # Father gets residue if no sons
            fractions["Отец"] = "Остаток"
            if net_inheritance > 0:
                percentages["Отец"] = (father_share / net_inheritance) * 100
            else:
                percentages["Отец"] = 0
            explanations["О доле отца"] = "Если у умершего нет сыновей, отец получает остаток наследства после распределения фиксированных долей другим наследникам. Согласно правилам 'асаба' (остаточные наследники), отец имеет право на оставшуюся часть наследства."
            
        amounts["Отец"] = father_share
        remaining -= father_share

    if user_data.get('has_mother', False):
        has_children = (user_data.get('num_sons', 0) > 0
                        or user_data.get('num_daughters', 0) > 0)
        has_siblings = (user_data.get('num_siblings_brothers', 0) > 0
                        or user_data.get('num_siblings_sisters', 0) > 0
                        or user_data.get('num_cousins_brothers', 0) > 0
                        or user_data.get('num_cousins_sisters', 0) > 0)

        if has_children or has_siblings:
            mother_share = net_inheritance * (1/6)
            fractions["Мать"] = "1/6"
            percentages["Мать"] = 16.67
            explanations["О доле матери"] = "Согласно аяту 11 суры Ан-Ниса (Женщины): «Каждому из родителей принадлежит одна шестая того, что он оставил, если у него есть ребенок. Если же у него есть братья, то матери достается одна шестая». Мать получает 1/6, так как у умершего есть дети или братья/сестры."
        else:
            mother_share = net_inheritance * (1/3)
            fractions["Мать"] = "1/3"
            percentages["Мать"] = 33.33
            explanations["О доле матери"] = "Согласно аяту 11 суры Ан-Ниса (Женщины): «Если же у него нет ребенка, то ему наследуют родители, и матери достается одна треть». Мать получает 1/3, так как у умершего нет детей и братьев/сестер."

        amounts["Мать"] = mother_share
        remaining -= mother_share

    # Grandfather's share (paternal)
    if user_data.get('has_grandfather', False):
        if user_data.get('has_father', False):
            # Grandfather doesn't inherit if father is alive
            explanations["Дедушка (по отцу)"] = "Не получает долю, так как отец жив. По исламскому праву, наличие отца блокирует право деда на наследство, поскольку отец является более близким родственником к умершему."
        else:
            # If father is not alive, grandfather gets 1/6
            grandfather_share = net_inheritance * (1/6)
            amounts["Дедушка (по отцу)"] = grandfather_share
            fractions["Дедушка (по отцу)"] = "1/6"
            percentages["Дедушка (по отцу)"] = 16.67
            explanations["О доле дедушки"] = "В отсутствие отца, дедушка (по отцовской линии) занимает его место в наследовании и получает фиксированную долю 1/6 наследства. Это правило основано на принципе 'асабы' - когда более близкий родственник отсутствует, его место занимает следующий по степени родства."
            remaining -= grandfather_share

    # Grandmother's share (maternal)
    if user_data.get('has_grandmother', False):
        if user_data.get('has_mother', False):
            # Grandmother doesn't inherit if mother is alive
            explanations["Бабушка (по матери)"] = "Не получает долю, так как мать жива. По исламскому праву, наличие матери блокирует право бабушки на наследство, поскольку мать является более близким родственником к умершему."
        else:
            # If mother is not alive, grandmother gets 1/6
            grandmother_share = net_inheritance * (1/6)
            amounts["Бабушка (по матери)"] = grandmother_share
            fractions["Бабушка (по матери)"] = "1/6"
            percentages["Бабушка (по матери)"] = 16.67
            explanations["О доле бабушки"] = "В отсутствие матери, бабушка (по материнской линии) занимает её место в наследовании и получает фиксированную долю 1/6 наследства. Это правило основано на хадисе, согласно которому Пророк Мухаммад (мир ему) установил для бабушки 1/6 часть наследства, если нет матери."
            remaining -= grandmother_share

    # Children shares
    num_sons = user_data.get('num_sons', 0)
    num_daughters = user_data.get('num_daughters', 0)

    if num_sons > 0 or num_daughters > 0:
        # In Islamic law, a son gets twice the share of a daughter
        total_parts = num_sons * 2 + num_daughters
        explanations["О доле детей"] = "Согласно аяту 11 суры Ан-Ниса (Женщины): «Аллах заповедует вам относительно ваших детей: мужчине достается доля, равная доле двух женщин». Сыновья и дочери получают остаток наследства после распределения фиксированных долей другим наследникам, при этом доля сына вдвое больше доли дочери."

        if total_parts > 0:
            share_per_part = remaining / total_parts

            if num_sons > 0:
                son_share = share_per_part * 2
                son_percentage = (son_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                
                if num_sons > 1:
                    amounts[f"Сыновья ({num_sons})"] = son_share * num_sons
                    amounts[f"Каждому сыну"] = son_share
                    fractions[f"Каждому сыну"] = f"{2}/{total_parts} остатка"
                    percentages[f"Каждому сыну"] = son_percentage
                else:
                    amounts["Сын"] = son_share
                    fractions["Сын"] = f"{2}/{total_parts} остатка"
                    percentages["Сын"] = son_percentage

            if num_daughters > 0:
                daughter_share = share_per_part
                daughter_percentage = (daughter_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                
                if num_daughters > 1:
                    amounts[f"Дочери ({num_daughters})"] = daughter_share * num_daughters
                    amounts[f"Каждой дочери"] = daughter_share
                    fractions[f"Каждой дочери"] = f"1/{total_parts} остатка"
                    percentages[f"Каждой дочери"] = daughter_percentage
                else:
                    amounts["Дочь"] = daughter_share
                    fractions["Дочь"] = f"1/{total_parts} остатка"
                    percentages["Дочь"] = daughter_percentage

            remaining = 0  # All remaining inheritance distributed

    # Check if there are grandsons/granddaughters but they don't inherit
    num_grandsons = user_data.get('num_grandsons', 0)
    num_granddaughters = user_data.get('num_granddaughters', 0)
    
    # If there are grandsons/granddaughters but they don't inherit (because there are sons/daughters)
    if (num_sons > 0 or num_daughters > 0) and (num_grandsons > 0 or num_granddaughters > 0):
        if num_grandsons > 0:
            if num_grandsons > 1:
                explanations[f"Внуки ({num_grandsons})"] = "Не получают долю, так как есть сыновья/дочери покойного"
            else:
                explanations["Внук"] = "Не получает долю, так как есть сыновья/дочери покойного"
        
        if num_granddaughters > 0:
            if num_granddaughters > 1:
                explanations[f"Внучки ({num_granddaughters})"] = "Не получают долю, так как есть сыновья/дочери покойного"
            else:
                explanations["Внучка"] = "Не получает долю, так как есть сыновья/дочери покойного"
    
    # If no children, distribute to grandchildren
    if num_sons == 0 and num_daughters == 0 and remaining > 0:
        if num_grandsons > 0 or num_granddaughters > 0:
            total_parts = num_grandsons * 2 + num_granddaughters
            explanations["О доле внуков"] = "В отсутствие сыновей и дочерей, внуки и внучки занимают их место в наследовании. По принципу 'таазиб', действует то же правило, как и для детей: внук получает вдвое больше, чем внучка. Внуки наследуют остаток имущества после распределения фиксированных долей другим наследникам."

            if total_parts > 0:
                share_per_part = remaining / total_parts

                if num_grandsons > 0:
                    grandson_share = share_per_part * 2
                    grandson_percentage = (grandson_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                    
                    if num_grandsons > 1:
                        amounts[f"Внуки ({num_grandsons})"] = grandson_share * num_grandsons
                        amounts[f"Каждому внуку"] = grandson_share
                        fractions[f"Каждому внуку"] = f"{2}/{total_parts} остатка"
                        percentages[f"Каждому внуку"] = grandson_percentage
                    else:
                        amounts["Внук"] = grandson_share
                        fractions["Внук"] = f"{2}/{total_parts} остатка"
                        percentages["Внук"] = grandson_percentage

                if num_granddaughters > 0:
                    granddaughter_share = share_per_part
                    granddaughter_percentage = (granddaughter_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                    
                    if num_granddaughters > 1:
                        amounts[f"Внучки ({num_granddaughters})"] = granddaughter_share * num_granddaughters
                        amounts[f"Каждой внучке"] = granddaughter_share
                        fractions[f"Каждой внучке"] = f"1/{total_parts} остатка"
                        percentages[f"Каждой внучке"] = granddaughter_percentage
                    else:
                        amounts["Внучка"] = granddaughter_share
                        fractions["Внучка"] = f"1/{total_parts} остатка"
                        percentages["Внучка"] = granddaughter_percentage

                remaining = 0  # All remaining inheritance distributed

    # Check if there are sons, daughters, grandsons, or granddaughters that would block siblings and cousins inheritance
    has_direct_descendants = (
        user_data.get('num_sons', 0) > 0 or 
        user_data.get('num_daughters', 0) > 0 or 
        user_data.get('num_grandsons', 0) > 0 or 
        user_data.get('num_granddaughters', 0) > 0
    )
    
    # Get number of siblings
    num_siblings_brothers = user_data.get('num_siblings_brothers', 0)
    num_siblings_sisters = user_data.get('num_siblings_sisters', 0)
    
    # Get number of cousins
    num_brothers = user_data.get('num_cousins_brothers', 0)
    num_sisters = user_data.get('num_cousins_sisters', 0)
    
    # Check if there are siblings but they wouldn't inherit due to direct descendants
    if has_direct_descendants and (num_siblings_brothers > 0 or num_siblings_sisters > 0):
        if num_siblings_brothers > 0:
            if num_siblings_brothers > 1:
                explanations[f"Родные братья ({num_siblings_brothers})"] = "Не получают долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
            else:
                explanations["Родной брат"] = "Не получает долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
        
        if num_siblings_sisters > 0:
            if num_siblings_sisters > 1:
                explanations[f"Родные сестры ({num_siblings_sisters})"] = "Не получают долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
            else:
                explanations["Родная сестра"] = "Не получает долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
    
    # Check if there are cousins but they wouldn't inherit due to direct descendants
    if has_direct_descendants and (num_brothers > 0 or num_sisters > 0):
        if num_brothers > 0:
            if num_brothers > 1:
                explanations[f"Двоюродные братья ({num_brothers})"] = "Не получают долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
            else:
                explanations["Двоюродный брат"] = "Не получает долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
        
        if num_sisters > 0:
            if num_sisters > 1:
                explanations[f"Двоюродные сестры ({num_sisters})"] = "Не получают долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
            else:
                explanations["Двоюродная сестра"] = "Не получает долю, так как есть прямые потомки (сыновья/дочери/внуки/внучки)"
    
    # Особое правило для сестер: если нет братьев, сыновей и отца, сестра получает 1/2, две и более сестер - 2/3
    special_sisters_rule = (
        not has_direct_descendants and  # Нет сыновей, дочерей, внуков и внучек
        num_siblings_brothers == 0 and  # Нет братьев
        num_siblings_sisters > 0 and    # Есть сестры
        not user_data.get('has_father', False)  # Нет отца
    )
    
    # Сперва распределяем наследство родным братьям и сестрам, если они есть
    if remaining > 0:
        if num_siblings_brothers > 0 or num_siblings_sisters > 0:
            # Применяем особое правило для сестер, если условия соответствуют
            if special_sisters_rule:
                explanations["О доле сестер"] = "Согласно аяту 176 суры Ан-Ниса (Женщины): «Если умрет мужчина, у которого нет ребенка, но есть сестра, то ей принадлежит половина того, что он оставил. И он наследует ей, если у нее нет ребенка. Если их две, то им принадлежат две трети того, что он оставил»."
                
                if num_siblings_sisters == 1:  # Одна сестра получает 1/2
                    sister_share = net_inheritance * 0.5
                    amounts["Родная сестра"] = sister_share
                    fractions["Родная сестра"] = "1/2"
                    percentages["Родная сестра"] = 50.0
                    remaining -= sister_share
                else:  # Две и более сестер делят 2/3
                    total_share = net_inheritance * (2/3)
                    each_sister_share = total_share / num_siblings_sisters
                    amounts[f"Родные сестры ({num_siblings_sisters})"] = total_share
                    amounts[f"Каждой родной сестре"] = each_sister_share
                    fractions[f"Каждой родной сестре"] = f"2/3 ÷ {num_siblings_sisters}"
                    percentages[f"Каждой родной сестре"] = (each_sister_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                    remaining -= total_share
            else:
                # Стандартный расчет: брат получает в два раза больше сестры
                total_parts = num_siblings_brothers * 2 + num_siblings_sisters
                explanations["О доле братьев и сестер"] = "Согласно аяту 176 суры Ан-Ниса (Женщины): «Если они являются братьями и сестрами, то мужчине принадлежит доля, равная доле двух женщин». Братья и сестры наследуют при отсутствии прямых потомков (сыновей и дочерей) умершего, при этом брат получает долю в два раза больше, чем сестра."
    
                if total_parts > 0:
                    share_per_part = remaining / total_parts
    
                    if num_siblings_brothers > 0:
                        brother_share = share_per_part * 2
                        brother_percentage = (brother_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                        
                        if num_siblings_brothers > 1:
                            amounts[f"Родные братья ({num_siblings_brothers})"] = brother_share * num_siblings_brothers
                            amounts[f"Каждому родному брату"] = brother_share
                            fractions[f"Каждому родному брату"] = f"{2}/{total_parts} остатка"
                            percentages[f"Каждому родному брату"] = brother_percentage
                        else:
                            amounts["Родной брат"] = brother_share
                            fractions["Родной брат"] = f"{2}/{total_parts} остатка"
                            percentages["Родной брат"] = brother_percentage
    
                    if num_siblings_sisters > 0:
                        sister_share = share_per_part
                        sister_percentage = (sister_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                        
                        if num_siblings_sisters > 1:
                            amounts[f"Родные сестры ({num_siblings_sisters})"] = sister_share * num_siblings_sisters
                            amounts[f"Каждой родной сестре"] = sister_share
                            fractions[f"Каждой родной сестре"] = f"1/{total_parts} остатка"
                            percentages[f"Каждой родной сестре"] = sister_percentage
                        else:
                            amounts["Родная сестра"] = sister_share
                            fractions["Родная сестра"] = f"1/{total_parts} остатка"
                            percentages["Родная сестра"] = sister_percentage
    
                    remaining = 0  # All remaining inheritance distributed
    
    # Если после распределения родным братьям и сестрам остались средства, распределяем двоюродным
    if remaining > 0:
        if num_brothers > 0 or num_sisters > 0:
            total_parts = num_brothers * 2 + num_sisters

            if total_parts > 0:
                share_per_part = remaining / total_parts

                if num_brothers > 0:
                    brother_share = share_per_part * 2
                    brother_percentage = (brother_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                    
                    if num_brothers > 1:
                        amounts[f"Двоюродные братья ({num_brothers})"] = brother_share * num_brothers
                        amounts[f"Каждому двоюродному брату"] = brother_share
                        fractions[f"Каждому двоюродному брату"] = f"{2}/{total_parts} остатка"
                        percentages[f"Каждому двоюродному брату"] = brother_percentage
                    else:
                        amounts["Двоюродный брат"] = brother_share
                        fractions["Двоюродный брат"] = f"{2}/{total_parts} остатка"
                        percentages["Двоюродный брат"] = brother_percentage

                if num_sisters > 0:
                    sister_share = share_per_part
                    sister_percentage = (sister_share / net_inheritance) * 100 if net_inheritance > 0 else 0
                    
                    if num_sisters > 1:
                        amounts[f"Двоюродные сестры ({num_sisters})"] = sister_share * num_sisters
                        amounts[f"Каждой двоюродной сестре"] = sister_share
                        fractions[f"Каждой двоюродной сестре"] = f"1/{total_parts} остатка"
                        percentages[f"Каждой двоюродной сестре"] = sister_percentage
                    else:
                        amounts["Двоюродная сестра"] = sister_share
                        fractions["Двоюродная сестра"] = f"1/{total_parts} остатка"
                        percentages["Двоюродная сестра"] = sister_percentage

                remaining = 0  # All remaining inheritance distributed
    
    # Если есть двоюродные братья/сестры, но родные братья/сестры уже получили наследство
    if num_siblings_brothers > 0 or num_siblings_sisters > 0:
        if num_brothers > 0:
            if num_brothers > 1:
                explanations[f"Двоюродные братья ({num_brothers})"] = "Не получают долю, так как есть родные братья/сестры"
            else:
                explanations["Двоюродный брат"] = "Не получает долю, так как есть родные братья/сестры"
        
        if num_sisters > 0:
            if num_sisters > 1:
                explanations[f"Двоюродные сестры ({num_sisters})"] = "Не получают долю, так как есть родные братья/сестры"
            else:
                explanations["Двоюродная сестра"] = "Не получает долю, так как есть родные братья/сестры"

    # Возвращаем словарь с разными типами представления долей
    return {
        'amounts': amounts,  # Денежные суммы
        'fractions': fractions,  # Дроби по исламскому праву
        'percentages': percentages,  # Проценты
        'explanations': explanations  # Объяснения для наследников без доли
    }


# Функция для получения эмодзи в зависимости от типа наследника
def get_emoji_for_heir(heir_name):
    if "завещание" in heir_name.lower() or "васия" in heir_name.lower():
        return "📜"
    elif "муж" in heir_name.lower():
        return "👨‍❤️‍👨"
    elif "жена" in heir_name.lower():
        return "👩‍❤️‍👨"
    elif "сын" in heir_name.lower():
        return "👦"
    elif "дочь" in heir_name.lower() or "дочер" in heir_name.lower():
        return "👧"
    elif "отец" in heir_name.lower():
        return "👨‍🦳"
    elif "мать" in heir_name.lower() or "матер" in heir_name.lower():
        return "👩‍🦳"
    elif "дедушк" in heir_name.lower():
        return "👴"
    elif "бабушк" in heir_name.lower():
        return "👵"
    elif "двоюродный брат" in heir_name.lower() or "двоюродные братья" in heir_name.lower():
        return "👬"
    elif "двоюродная сестра" in heir_name.lower() or "двоюродные сестры" in heir_name.lower():
        return "👭"
    elif "брат" in heir_name.lower():
        return "👬"
    elif "сестр" in heir_name.lower():
        return "👭"
    elif "внук" in heir_name.lower() and not "внучк" in heir_name.lower():
        return "👦"
    elif "внучк" in heir_name.lower():
        return "👧"
    else:
        return "👤"


def format_inheritance_response(user_data, shares_data):
    """Format the inheritance calculation results for display."""
    total_inheritance = float(user_data.get('total_inheritance', 0))
    debts = float(user_data.get('debts', 0))
    has_will = user_data.get('has_will', False)
    will_amount = float(user_data.get('will_amount', 0)) if has_will else 0
    net_inheritance = total_inheritance - debts

    # Проверяем структуру данных
    if isinstance(shares_data, dict) and 'amounts' in shares_data:
        # Новый формат данных
        amounts = shares_data.get('amounts', {})
        fractions = shares_data.get('fractions', {})
        percentages = shares_data.get('percentages', {})
        explanations = shares_data.get('explanations', {})
    else:
        # Старый формат данных (обратная совместимость)
        amounts = shares_data
        fractions = {}
        percentages = {}
        explanations = {}

    response = "📋 *РЕЗУЛЬТАТЫ РАСЧЕТА НАСЛЕДСТВА*\n\n"
    response += f"💰 *Общая сумма наследства:* {total_inheritance:.2f} ₽\n"
    response += f"💸 *Долги:* {debts:.2f} ₽\n"
    
    if has_will and will_amount > 0:
        response += f"📜 *Сумма по завещанию:* {will_amount:.2f} ₽ (≤1/3 от наследства)\n"
    
    response += f"🏦 *Чистая сумма для распределения:* {net_inheritance:.2f} ₽\n\n"
    response += "*Распределение наследства:*\n\n"

    if not amounts:
        response += "❌ Не удалось рассчитать доли наследства.\n"
    else:
        # Сортируем наследников для лучшего представления
        for heir in sorted(amounts.keys()):
            amount = amounts[heir]
            # Обрабатываем значение, чтобы убедиться, что это число
            try:
                if isinstance(amount, (int, float)):
                    amount_value = amount
                else:
                    amount_value = float(amount)
                
                # Получаем эмодзи для наследника
                heir_emoji = get_emoji_for_heir(heir)
                
                # Начинаем раздел для каждого наследника с эмодзи
                response += f"{heir_emoji} *{heir}:*\n"
                
                # Добавляем информацию о сумме
                response += f"• 💰 Сумма: {amount_value:.2f} ₽\n"
                
                # Добавляем процентное соотношение
                if heir in percentages:
                    response += f"• 📊 Процент: {percentages[heir]:.2f}%\n"
                else:
                    # Вычисляем процент, если он не предоставлен
                    percentage = (amount_value / net_inheritance) * 100 if net_inheritance > 0 else 0
                    response += f"• 📊 Процент: {percentage:.2f}%\n"
                
                # Добавляем исламскую долю
                if heir in fractions:
                    response += f"• ⚖️ Исламская доля: {fractions[heir]}\n"
                else:
                    response += f"• ⚖️ Исламская доля: Расчетная доля\n"
                
                response += "\n"
            except (ValueError, TypeError):
                # Получаем эмодзи для наследника и добавляем сообщение об ошибке
                heir_emoji = get_emoji_for_heir(heir)
                response += f"{heir_emoji} *{heir}:* {amount}\n\n"

    # Добавляем информацию о наследниках, которые не получают доли
    if explanations:
        response += "*Наследники без доли:*\n\n"
        for heir, explanation in sorted(explanations.items()):
            heir_emoji = get_emoji_for_heir(heir)
            response += f"{heir_emoji} *{heir}:* {explanation}\n\n"

    response += "✅ Расчет выполнен согласно исламским законам наследования.\n"
    response += "ℹ️ Для нового расчета используйте команду /start\n"
    response += "💰 Чтобы поддержать проект: используйте кнопку \"Донат\"\n"
    response += "💬 Для отзывов и предложений: используйте кнопку \"Отзывы и предложения\""

    return response


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    # Создаем клавиатуру с кнопками
    keyboard = [
        [KeyboardButton('🧮 Начать расчет')],
        [KeyboardButton('💰 Донат'), KeyboardButton('💬 Отзывы и предложения')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        'Расчет отменен. Чтобы начать снова, используйте кнопку "Начать расчет" или команду /start',
        reply_markup=reply_markup)
    return ConversationHandler.END


def error_handler(update, context):
    """Log errors caused by updates."""
    error_message = str(context.error)
    logger.warning(f'Update "{update}" caused error "{error_message}"')
    
    # Игнорируем ошибку конфликта при запуске нескольких экземпляров бота
    if "Conflict: terminated by other getUpdates request" in error_message:
        logger.info("Обнаружен другой экземпляр бота, работающий с тем же токеном.")
        logger.info("Возможные решения: 1) Остановите другой экземпляр бота; 2) Используйте другой токен бота для этого экземпляра")
        return
    
    # Обрабатываем ошибку тайм-аута
    if "Timed out" in error_message or (hasattr(context.error, '__class__') and context.error.__class__.__name__ == 'TimedOut'):
        logger.info("Произошёл тайм-аут при подключении к Telegram API. Подождите, бот автоматически попробует переподключиться.")
        return
        
    # Обрабатываем другие сетевые ошибки
    if (hasattr(context.error, '__class__') and context.error.__class__.__name__ == 'NetworkError'):
        logger.info("Произошла сетевая ошибка. Бот автоматически попробует переподключиться.")
        return
        
    # Обрабатываем ошибку аутентификации
    if "Unauthorized" in error_message:
        logger.error("Ошибка авторизации! Проверьте токен бота (TELEGRAM_BOT_TOKEN).")
        return
    
    # Оба дополнительных условия нужны для защиты от возможных ошибок
    try:
        if update and hasattr(update, 'message') and update.message:
            update.message.reply_text(
                'Произошла ошибка. Пожалуйста, начните снова с команды /start')
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок: {e}")


def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    # Создаем клавиатуру с кнопками
    keyboard = [
        [KeyboardButton('🧮 Начать расчет')],
        [KeyboardButton('💰 Донат'), KeyboardButton('💬 Отзывы и предложения')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        '📊 *Калькулятор наследства PRO* 📊\n\n'
        'Этот бот помогает рассчитать доли наследства по исламским законам наследования (фараиз).\n\n'
        '*Возможности PRO-версии:*\n'
        '• Расчет долей наследства по исламским правилам\n'
        '• Учет долгов наследодателя\n'
        '• Поддержка исламского завещания (васия)\n'
        '• Специальные правила для особых случаев\n'
        '• Лишение доли убийце наследодателя\n'
        '• Учет различий в вере между наследниками\n'
        '• Особые правила для сестер при отсутствии братьев и сыновей\n\n'
        'Для начала расчета нажмите кнопку "Начать расчет" или используйте команду /start.\n'
        'Вам нужно будет ответить на серию вопросов о наследодателе и его семье.',
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


def donate_command(update: Update, context: CallbackContext):
    """Send donation information when the donate button is pressed."""
    update.message.reply_text(
        '💰 *Поддержать проект*\n\n'
        'Если вам понравился наш бот, вы можете поддержать его развитие:\n\n'
        '*Реквизиты для доната:*\n'
        '📌 2202202342072935 (МИР Сбербанк)\n\n'
        'Спасибо за вашу поддержку! ❤️',
        parse_mode='Markdown'
    )


def feedback_command(update: Update, context: CallbackContext):
    """Send feedback information when the feedback button is pressed."""
    update.message.reply_text(
        '💬 *Отзывы и предложения*\n\n'
        'Мы будем рады услышать ваши отзывы и предложения по улучшению бота!\n\n'
        'Пожалуйста, напишите ваш отзыв в ответном сообщении, и мы постараемся учесть его при дальнейшей разработке.',
        parse_mode='Markdown'
    )


def main():
    """Start the bot."""
    # Get the token from environment variables
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    # Check if token exists
    if not TOKEN:
        logger.error("Отсутствует TELEGRAM_BOT_TOKEN. Убедитесь, что переменная окружения установлена.")
        return
        
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOTAL_INHERITANCE: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_total_inheritance)
            ],
            DEBTS:
            [MessageHandler(Filters.text & ~Filters.command, handle_debts)],
            HAS_WILL: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_has_will)
            ],
            WILL_AMOUNT: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_will_amount)
            ],
            IS_MURDERER: [
                MessageHandler(Filters.text & ~Filters.command,
                              handle_is_murderer)
            ],
            IS_DIFFERENT_FAITH: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_is_different_faith)
            ],
            HAS_SPOUSE: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_has_spouse)
            ],
            HAS_WIFE:
            [MessageHandler(Filters.text & ~Filters.command, handle_has_wife)],
            NUM_DAUGHTERS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_daughters)
            ],
            NUM_SONS:
            [MessageHandler(Filters.text & ~Filters.command, handle_num_sons)],
            NUM_GRANDDAUGHTERS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_granddaughters)
            ],
            NUM_GRANDSONS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_grandsons)
            ],
            HAS_FATHER: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_has_father)
            ],
            HAS_MOTHER: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_has_mother)
            ],
            HAS_GRANDFATHER: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_has_grandfather)
            ],
            HAS_GRANDMOTHER: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_has_grandmother)
            ],
            NUM_SIBLINGS_SISTERS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_siblings_sisters)
            ],
            NUM_SIBLINGS_BROTHERS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_siblings_brothers)
            ],
            NUM_COUSINS_SISTERS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_cousins_sisters)
            ],
            NUM_COUSINS_BROTHERS: [
                MessageHandler(Filters.text & ~Filters.command,
                               handle_num_cousins_brothers)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # Add handlers for the buttons
    dispatcher.add_handler(MessageHandler(Filters.regex('^🧮 Начать расчет$'), start))
    dispatcher.add_handler(MessageHandler(Filters.regex('^💰 Донат$'), donate_command))
    dispatcher.add_handler(MessageHandler(Filters.regex('^💬 Отзывы и предложения$'), feedback_command))

    # Register error handler
    dispatcher.add_error_handler(error_handler)

    # Start the Bot with improved configuration to handle network issues
    # - drop_pending_updates=True: избегаем конфликтов при перезапуске
    # - timeout=30: увеличенный таймаут для сетевых операций
    
    # Запуск бота с базовыми параметрами, которые поддерживаются в текущей версии
    updater.start_polling(drop_pending_updates=True, timeout=30)
    
    logger.info("Бот успешно запущен!")

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
