from fastapi import HTTPException, status



UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Пользователь уже существует'
)

IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Неверная почта или пароль',
)

TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Токен истек',
)

TokenAbsentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Токен отсутствует',
)

IncorrectFormatTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Неверный формат токена',
)

ErrorProfileException = HTTPException(
    status_code=500, detail="Произошла ошибка при получении профиля."
)

ErrorGettingDetailsException = HTTPException(
    status_code=500, detail="Ошибка при выполнении запроса на получение деталей фильма."
)

ErrorWithResponseException = HTTPException(
    status_code=500, detail="Ошибка при выполнении запроса на поиск фильмов."
)

UnexpectedResponseFormatException = HTTPException(
    status_code=500, detail="Неожиданный формат ответа от API Кинопоиска"
)

NoMovieIDException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Id с таким фильмом нет"
)

NetworkErrorException = HTTPException(
    status_code=503, detail="Ошибка сети, повторите попытку позже"
) 

EnternalServerErrorException = HTTPException(
    status_code=500, detail="Внутренняя ошибка сервера"
)

ErrorWithEntranceException = HTTPException(
    status_code=500, detail="Произошла ошибка при входе."
)

ErrorWithRegisterException = HTTPException(
    status_code=500, detail="Произошла ошибка при регистрации."
)

UserIsNotPresentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
)

DontMatchPassExceptions = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail='Пароли не совпадают'
) 

NoUserExceptions = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail='Нет аутентифицированного пользователя'
)

UnexpectedStructureException = HTTPException(
    status_code=500, detail="Непредвиденная структура ответа: 'films' не является списком."
)  

FilmNotFoundException = HTTPException( 
    status_code=status.HTTP_404_NOT_FOUND, 
    detail='Фильм не найден' 
) 
 
ExternalAPIException = HTTPException( 
    status_code=status.HTTP_502_BAD_GATEWAY, 
    detail='Ошибка при обращении к внешнему API' 
) 
 
InvalidKinopoiskIDException = HTTPException( 
    status_code=status.HTTP_400_BAD_REQUEST, 
    detail='Неверный Kinopoisk ID', 
)