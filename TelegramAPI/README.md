## Описание
Inline-бот, написанный на чистом API Телеграма.

## Запуск
```
cli.py BOT_TOKEN
```
**BOT_TOKEN** - токен, который выдается @BotFather при создании бота

## Использование
```
@UserDescriberBot [some_text]
```
Позволяет отправить в какой-либо чат сообщение - **some_text** - с преложенными к нему кнопками "Give" и "Deny". При нажатии на первую кнопку, текст сообщения изменится на информацию (fullname, username, id) о пользователе, нажавшем кнопку; при нажатии на вторую кнопку, текст изменится на сообщение "Access is denied".

В случае, если параметр "some_text" опущен, в тексте сообщения будет написано следующее:
> Press to the "Give" button to see basic information (fullname, username, id) about you telegram account