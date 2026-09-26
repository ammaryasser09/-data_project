# -*- coding: utf-8 -*-
"""
Multi-turn conversation templates (v4) for the 30 service flows INT009–INT014 × F1–F5,
in English, Arabic (MSA), French, Russian and Egyptian Arabic.

Every template is a list of turns alternating user / assistant, starting with the user.
Slots in {BRACES} are filled by generate_conversations.py from the operational database,
so every booking, room, date, rate and member quoted is real. A turn given as a dict
{'fit': ..., 'over': ...} or {'mem': ..., 'non': ...} is a branch chosen by the data.
OPENERS gives three first turns for flows that quote no database record, so their three
variants differ.
"""
L = ('English', 'Arabic', 'French', 'Russian', 'Arabic-Egyptian')

TYPE = {
 'English': {'RT001': 'Single Room', 'RT002': 'Double Room', 'RT003': 'Twin Room', 'RT004': 'Deluxe Room', 'RT005': 'Family Room', 'RT006': 'Suite'},
 'Arabic': {'RT001': 'غرفة مفردة', 'RT002': 'غرفة مزدوجة', 'RT003': 'غرفة بسريرين', 'RT004': 'غرفة ديلوكس', 'RT005': 'غرفة عائلية', 'RT006': 'جناح'},
 'French': {'RT001': 'chambre Single', 'RT002': 'chambre Double', 'RT003': 'chambre Twin', 'RT004': 'chambre Deluxe', 'RT005': 'chambre Familiale', 'RT006': 'Suite'},
 'Russian': {'RT001': 'одноместный номер', 'RT002': 'номер Double', 'RT003': 'номер Twin', 'RT004': 'номер Делюкс', 'RT005': 'семейный номер', 'RT006': 'люкс'},
 'Arabic-Egyptian': {'RT001': 'أوضة سينجل', 'RT002': 'أوضة دبل', 'RT003': 'أوضة بسريرين', 'RT004': 'أوضة ديلوكس', 'RT005': 'أوضة عائلية', 'RT006': 'جناح'},
}
TIER = {
 'English': {'Silver': 'Silver', 'Gold': 'Gold', 'Platinum': 'Platinum'},
 'Arabic': {'Silver': 'الفضي', 'Gold': 'الذهبي', 'Platinum': 'البلاتيني'},
 'French': {'Silver': 'Silver', 'Gold': 'Gold', 'Platinum': 'Platinum'},
 'Russian': {'Silver': 'Silver', 'Gold': 'Gold', 'Platinum': 'Platinum'},
 'Arabic-Egyptian': {'Silver': 'الفضي', 'Gold': 'الدهبي', 'Platinum': 'البلاتيني'},
}

T = {}
OPENERS = {}

# ───────────────────────── INT009 booking modifications ─────────────────────────
T['INT009_F1'] = {
'English': ["I need to make a change to my reservation.",
 "Of course. What would you like to change — the dates, the room type or the number of guests? And what is your booking reference?",
 "It's {BID}. I'd like to arrive on {NCI} instead.",
 "Booking {BID} is a {TYPE} from {CI} to {CO}, {N} nights. Moving it to {NCI} – {NCO} keeps the same number of nights. It is on the {RP} rate and more than 48 hours before arrival, so the change is free; it depends on availability for the new dates, and any difference in rate will be confirmed before anything is charged. Shall I submit the request?",
 "Yes, please submit it.",
 "Done. The date-change request for {BID} has been submitted, and you will receive confirmation once the hotel approves it."],
'Arabic': ["أحتاج إلى تعديل حجزي.",
 "بالتأكيد. ما الذي تريد تعديله: التواريخ أم نوع الغرفة أم عدد النزلاء؟ وما رقم الحجز؟",
 "رقم الحجز {BID}، وأريد أن يكون الوصول يوم {NCI} بدلاً من ذلك.",
 "الحجز {BID} هو {TYPE} من {CI} إلى {CO}، وعدد الليالي {N}. نقله إلى الفترة من {NCI} إلى {NCO} يحافظ على عدد الليالي نفسه. الحجز بالسعر {RP} وقبل الوصول بأكثر من 48 ساعة، لذا فالتعديل مجاني، ويخضع للتوافر في التواريخ الجديدة، وسيُؤكَّد أي فرق في السعر قبل أي خصم. هل أرسل الطلب؟",
 "نعم، أرسل الطلب من فضلك.",
 "تم. أُرسل طلب تغيير التواريخ للحجز {BID}، وستصلك رسالة تأكيد بعد موافقة الفندق."],
'French': ["J'ai besoin de modifier ma réservation.",
 "Bien sûr. Que souhaitez-vous modifier : les dates, le type de chambre ou le nombre de personnes ? Et quel est votre numéro de réservation ?",
 "C'est {BID}. Je voudrais arriver le {NCI} à la place.",
 "La réservation {BID} est une {TYPE} du {CI} au {CO}, soit {N} nuits. La déplacer du {NCI} au {NCO} conserve le même nombre de nuits. Elle est au tarif {RP} et à plus de 48 heures de l'arrivée, donc la modification est gratuite ; elle dépend de la disponibilité aux nouvelles dates, et toute différence de tarif sera confirmée avant tout débit. Dois-je envoyer la demande ?",
 "Oui, envoyez-la s'il vous plaît.",
 "C'est fait. La demande de changement de dates pour {BID} a été envoyée ; vous recevrez une confirmation dès que l'hôtel l'aura approuvée."],
'Russian': ["Мне нужно изменить бронь.",
 "Конечно. Что вы хотите изменить: даты, тип номера или количество гостей? И какой у вас номер брони?",
 "Бронь {BID}. Хочу заехать {NCI}.",
 "Бронь {BID}: {TYPE}, с {CI} по {CO}, количество ночей — {N}. Перенос на период с {NCI} по {NCO} сохраняет то же количество ночей. Тариф {RP}, до заезда больше 48 часов, поэтому изменение бесплатное; оно зависит от наличия мест на новые даты, а разницу в тарифе подтвердят до любого списания. Отправить запрос?",
 "Да, отправьте, пожалуйста.",
 "Готово. Запрос на изменение дат по брони {BID} отправлен, подтверждение придёт после одобрения отелем."],
'Arabic-Egyptian': ["محتاج أعدّل في الحجز بتاعي.",
 "أكيد. عايز تغير إيه: التواريخ ولا نوع الأوضة ولا عدد الأفراد؟ وقوللي رقم الحجز.",
 "رقم الحجز {BID}، وعايز أوصل يوم {NCI} بدل كده.",
 "الحجز {BID} {TYPE} من {CI} لـ {CO}، وعدد الليالي {N}. لو نقلناه من {NCI} لـ {NCO} هيفضل نفس عدد الليالي. الحجز بالسعر {RP} ولسه فاضل أكتر من 48 ساعة على الوصول، فالتغيير ببلاش، على حسب المتاح في التواريخ الجديدة، وأي فرق في السعر هيتأكدلك قبل ما يتخصم حاجة. أبعت الطلب؟",
 "أيوة ابعته لو سمحت.",
 "تمام، طلب تغيير التواريخ للحجز {BID} اتبعت، وهيوصلك تأكيد أول ما الفندق يوافق."],
}
T['INT009_F2'] = {
'English': ["I need to leave a day earlier than planned.", "I can request that. What is your booking reference?", "{BID}.",
 "Booking {BID} is a {TYPE} from {CI} to {CO}. Checking out on {NCO} instead shortens it to {N2} nights. It is on the {RP} rate and more than 48 hours before arrival, so removing the night is free of charge. Shall I submit the change?",
 "Yes, go ahead.", "Submitted. The request to check out on {NCO} is with the hotel, and you will be notified once it is confirmed."],
'Arabic': ["أحتاج إلى المغادرة قبل موعدي بيوم.", "يمكنني طلب ذلك. ما رقم الحجز؟", "{BID}.",
 "الحجز {BID} هو {TYPE} من {CI} إلى {CO}. المغادرة يوم {NCO} تجعل عدد الليالي {N2}. الحجز بالسعر {RP} وقبل الوصول بأكثر من 48 ساعة، لذا فإلغاء الليلة مجاني. هل أرسل التعديل؟",
 "نعم، تفضل.", "تم الإرسال. طلب المغادرة يوم {NCO} لدى الفندق الآن، وسيتم إبلاغك عند تأكيده."],
'French': ["Je dois partir un jour plus tôt que prévu.", "Je peux en faire la demande. Quel est votre numéro de réservation ?", "{BID}.",
 "La réservation {BID} est une {TYPE} du {CI} au {CO}. Partir le {NCO} ramène le séjour à {N2} nuits. Elle est au tarif {RP} et à plus de 48 heures de l'arrivée, donc retirer la nuit est gratuit. Dois-je envoyer la modification ?",
 "Oui, allez-y.", "C'est envoyé. La demande de départ le {NCO} est transmise à l'hôtel, et vous serez informé dès sa confirmation."],
'Russian': ["Мне нужно уехать на день раньше.", "Могу оформить запрос. Какой номер брони?", "{BID}.",
 "Бронь {BID}: {TYPE}, с {CI} по {CO}. При выезде {NCO} количество ночей станет {N2}. Тариф {RP}, до заезда больше 48 часов, поэтому снять ночь можно бесплатно. Отправить изменение?",
 "Да, отправьте.", "Отправлено. Запрос на выезд {NCO} передан в отель, вам сообщат после подтверждения."],
'Arabic-Egyptian': ["محتاج أمشي قبل ميعادي بيوم.", "أقدر أطلبهولك. رقم الحجز كام؟", "{BID}.",
 "الحجز {BID} {TYPE} من {CI} لـ {CO}. لو خرجت يوم {NCO} عدد الليالي هيبقى {N2}. الحجز بالسعر {RP} ولسه فاضل أكتر من 48 ساعة، فشيل الليلة ببلاش. أبعت التعديل؟",
 "أيوة ابعت.", "اتبعت. طلب الخروج يوم {NCO} عند الفندق دلوقتي، وهنبلغك أول ما يتأكد."],
}
T['INT009_F3'] = {
'English': ["I'd like to switch to a bigger room.", "I can request a room type change. What is your booking reference?", "{BID}.",
 "Booking {BID} is a {TYPE} from {CI} to {CO}. The next option up is a {ALT}, which holds up to {ALTCAP} guests at a standard rate of {ALTBASE} EGP per night. A room change depends on availability, and the final rate will be confirmed on approval. Shall I request the {ALT}?",
 "Yes, please.", "The request to change {BID} to a {ALT} has been submitted. The hotel will confirm availability and the new rate."],
'Arabic': ["أود الانتقال إلى غرفة أكبر.", "يمكنني طلب تغيير نوع الغرفة. ما رقم الحجز؟", "{BID}.",
 "الحجز {BID} هو {TYPE} من {CI} إلى {CO}. الخيار الأعلى التالي هو {ALT} بسعة قصوى {ALTCAP} وبسعر قياسي {ALTBASE} جنيه مصري لليلة. تغيير الغرفة يخضع للتوافر، وسيُؤكَّد السعر النهائي عند الموافقة. هل أطلب التغيير إلى {ALT}؟",
 "نعم، من فضلك.", "أُرسل طلب تغيير الحجز {BID} إلى {ALT}، وسيؤكد الفندق التوافر والسعر الجديد."],
'French': ["Je voudrais passer à une chambre plus grande.", "Je peux demander un changement de type de chambre. Quel est votre numéro de réservation ?", "{BID}.",
 "La réservation {BID} est une {TYPE} du {CI} au {CO}. L'option supérieure suivante est une {ALT}, d'une capacité de {ALTCAP} personnes, au tarif standard de {ALTBASE} EGP par nuit. Le changement dépend de la disponibilité, et le tarif final sera confirmé à l'approbation. Dois-je demander la {ALT} ?",
 "Oui, s'il vous plaît.", "La demande de passage de {BID} en {ALT} a été envoyée. L'hôtel confirmera la disponibilité et le nouveau tarif."],
'Russian': ["Я хотел бы перейти в номер побольше.", "Могу запросить смену типа номера. Какой номер брони?", "{BID}.",
 "Бронь {BID}: {TYPE}, с {CI} по {CO}. Следующий вариант — {ALT}, вместимость до {ALTCAP} гостей, стандартный тариф {ALTBASE} EGP за ночь. Смена номера зависит от наличия, итоговый тариф подтвердят при одобрении. Запросить {ALT}?",
 "Да, пожалуйста.", "Запрос на смену брони {BID} на {ALT} отправлен. Отель подтвердит наличие и новый тариф."],
'Arabic-Egyptian': ["عايز أنقل لأوضة أكبر.", "أقدر أطلبلك تغيير نوع الأوضة. رقم الحجز كام؟", "{BID}.",
 "الحجز {BID} {TYPE} من {CI} لـ {CO}. الاختيار اللي بعدها {ALT}، بتاخد لحد {ALTCAP} أفراد وسعرها الأساسي {ALTBASE} جنيه في الليلة. التغيير على حسب المتاح، والسعر النهائي هيتأكد لما الفندق يوافق. أطلبلك {ALT}؟",
 "أيوة لو سمحت.", "طلب تغيير الحجز {BID} لـ {ALT} اتبعت، والفندق هيأكدلك المتاح والسعر الجديد."],
}
T['INT009_F4'] = {
'English': ["One more person is joining my trip.", "I can check that against your room. What is your booking reference?", "{BID}. We'll be {NEWG} in total now.",
 {'fit': "Booking {BID} is a {TYPE} from {CI} to {CO}. It holds up to {CAP} guests, children included, so {NEWG} guests fit. I can submit the guest-count change for hotel approval. Shall I?",
  'over': "Booking {BID} is a {TYPE} from {CI} to {CO}. It holds up to {CAP} guests, children included, so {NEWG} guests would exceed it. A {ALT} holds up to {ALTCAP} guests at a standard rate of {ALTBASE} EGP per night. Shall I request a change to a {ALT}, subject to availability?"},
 "Yes, please.",
 {'fit': "Done — the change to {NEWG} guests on {BID} has been submitted, and the hotel will confirm it.",
  'over': "Done — the request to move {BID} to a {ALT} for {NEWG} guests has been submitted, subject to availability and hotel approval."}],
'Arabic': ["سينضم شخص آخر إلى رحلتي.", "يمكنني التحقق من ذلك مقارنةً بسعة غرفتك. ما رقم الحجز؟", "{BID}. سيصبح عددنا {NEWG}.",
 {'fit': "الحجز {BID} هو {TYPE} من {CI} إلى {CO}، وسعتها القصوى {CAP} بمن فيهم الأطفال، فالعدد {NEWG} مناسب. يمكنني إرسال طلب تغيير عدد النزلاء لموافقة الفندق. هل أرسله؟",
  'over': "الحجز {BID} هو {TYPE} من {CI} إلى {CO}، وسعتها القصوى {CAP} بمن فيهم الأطفال، لذا فالعدد {NEWG} يتجاوزها. {ALT} بسعة قصوى {ALTCAP} وبسعر قياسي {ALTBASE} جنيه مصري لليلة. هل أطلب التغيير إلى {ALT} حسب التوافر؟"},
 "نعم، من فضلك.",
 {'fit': "تم إرسال طلب تغيير عدد النزلاء في الحجز {BID} إلى {NEWG}، وسيؤكده الفندق.",
  'over': "تم إرسال طلب نقل الحجز {BID} إلى {ALT} لعدد {NEWG} من النزلاء، حسب التوافر وموافقة الفندق."}],
'French': ["Une personne de plus se joint à mon voyage.", "Je peux vérifier cela par rapport à votre chambre. Quel est votre numéro de réservation ?", "{BID}. Nous serons {NEWG} au total.",
 {'fit': "La réservation {BID} est une {TYPE} du {CI} au {CO}. Elle accueille jusqu'à {CAP} personnes, enfants compris, donc {NEWG} personnes y tiennent. Je peux envoyer la modification du nombre de personnes pour accord de l'hôtel. Je l'envoie ?",
  'over': "La réservation {BID} est une {TYPE} du {CI} au {CO}. Elle accueille jusqu'à {CAP} personnes, enfants compris, donc {NEWG} personnes dépasseraient sa capacité. Une {ALT} accueille jusqu'à {ALTCAP} personnes au tarif standard de {ALTBASE} EGP par nuit. Dois-je demander le passage en {ALT}, sous réserve de disponibilité ?"},
 "Oui, s'il vous plaît.",
 {'fit': "C'est fait — le passage à {NEWG} personnes sur {BID} a été envoyé, et l'hôtel le confirmera.",
  'over': "C'est fait — la demande de passage de {BID} en {ALT} pour {NEWG} personnes a été envoyée, sous réserve de disponibilité et d'accord de l'hôtel."}],
'Russian': ["К моей поездке присоединяется ещё один человек.", "Проверю, подходит ли номер. Какой номер брони?", "{BID}. Всего нас будет {NEWG}.",
 {'fit': "Бронь {BID}: {TYPE}, с {CI} по {CO}. Вместимость номера — {CAP}, включая детей, поэтому такое количество гостей подходит. Могу отправить изменение количества гостей на одобрение отеля. Отправить?",
  'over': "Бронь {BID}: {TYPE}, с {CI} по {CO}. Вместимость номера — {CAP}, включая детей, поэтому {NEWG} — больше допустимого. {ALT} вмещает до {ALTCAP} гостей, стандартный тариф {ALTBASE} EGP за ночь. Запросить смену на {ALT} при наличии мест?"},
 "Да, пожалуйста.",
 {'fit': "Готово — изменение количества гостей по брони {BID} отправлено, отель его подтвердит.",
  'over': "Готово — запрос на перевод брони {BID} в {ALT} отправлен, при наличии мест и с одобрения отеля."}],
'Arabic-Egyptian': ["في فرد زيادة هييجي معايا في الرحلة.", "أشوفلك الأوضة تساع ولا لأ. رقم الحجز كام؟", "{BID}. هنبقى {NEWG} أفراد.",
 {'fit': "الحجز {BID} {TYPE} من {CI} لـ {CO}، وبتاخد لحد {CAP} والأطفال محسوبين، يعني {NEWG} ينفعوا. أبعت طلب تغيير عدد الأفراد لموافقة الفندق؟",
  'over': "الحجز {BID} {TYPE} من {CI} لـ {CO}، وبتاخد لحد {CAP} بس والأطفال محسوبين، يعني {NEWG} أكتر من سعتها. {ALT} بتاخد لحد {ALTCAP} وسعرها الأساسي {ALTBASE} جنيه في الليلة. أطلبلك تغيير لـ {ALT} على حسب المتاح؟"},
 "أيوة لو سمحت.",
 {'fit': "تمام، طلب تغيير عدد الأفراد في الحجز {BID} اتبعت والفندق هيأكده.",
  'over': "تمام، طلب نقل الحجز {BID} لـ {ALT} لـ {NEWG} أفراد اتبعت، على حسب المتاح وموافقة الفندق."}],
}
T['INT009_F5'] = {
'English': ["I'd like to stay a couple more nights.", "Happy to request that. What is your booking reference?", "{BID}. Could I check out on {NCO}?",
 "Booking {BID} is a {TYPE} from {CI} to {CO} at {RATE} EGP per night. Checking out on {NCO} adds 2 nights. The extension depends on the room being free for those nights and on hotel approval, and the rate for the extra nights will be confirmed on approval. Shall I submit it?",
 "Yes, submit it.", "The extension of {BID} to {NCO} has been submitted. You will receive confirmation from the hotel."],
'Arabic': ["أود تمديد إقامتي ليلتين.", "يسعدني طلب ذلك. ما رقم الحجز؟", "{BID}. هل يمكن أن تكون المغادرة يوم {NCO}؟",
 "الحجز {BID} هو {TYPE} من {CI} إلى {CO} بسعر {RATE} جنيه مصري لليلة. المغادرة يوم {NCO} تضيف ليلتين. التمديد يخضع لتوفر الغرفة في هاتين الليلتين ولموافقة الفندق، وسيُؤكَّد سعر الليلتين الإضافيتين عند الموافقة. هل أرسل الطلب؟",
 "نعم، أرسله.", "تم إرسال طلب تمديد الحجز {BID} حتى {NCO}، وستصلك رسالة تأكيد من الفندق."],
'French': ["J'aimerais rester deux nuits de plus.", "Avec plaisir, je peux en faire la demande. Quel est votre numéro de réservation ?", "{BID}. Pourrais-je partir le {NCO} ?",
 "La réservation {BID} est une {TYPE} du {CI} au {CO} à {RATE} EGP par nuit. Partir le {NCO} ajoute 2 nuits. La prolongation dépend de la disponibilité de la chambre pour ces nuits et de l'accord de l'hôtel, et le tarif des nuits supplémentaires sera confirmé à l'approbation. Dois-je l'envoyer ?",
 "Oui, envoyez-la.", "La prolongation de {BID} jusqu'au {NCO} a été envoyée. L'hôtel vous enverra une confirmation."],
'Russian': ["Я хотел бы остаться ещё на две ночи.", "С удовольствием оформлю запрос. Какой номер брони?", "{BID}. Можно выехать {NCO}?",
 "Бронь {BID}: {TYPE}, с {CI} по {CO}, тариф {RATE} EGP за ночь. Выезд {NCO} добавляет 2 ночи. Продление зависит от того, свободен ли номер в эти ночи, и от одобрения отеля; тариф за дополнительные ночи подтвердят при одобрении. Отправить запрос?",
 "Да, отправьте.", "Запрос на продление брони {BID} до {NCO} отправлен. Отель пришлёт подтверждение."],
'Arabic-Egyptian': ["عايز أقعد ليلتين زيادة.", "أكيد أطلبهولك. رقم الحجز كام؟", "{BID}. ينفع أخرج يوم {NCO}؟",
 "الحجز {BID} {TYPE} من {CI} لـ {CO} بسعر {RATE} جنيه في الليلة. لو خرجت يوم {NCO} هتزيد ليلتين. التمديد على حسب إن الأوضة فاضية الليلتين دول وموافقة الفندق، وسعر الليلتين الزيادة هيتأكد لما الفندق يوافق. أبعت الطلب؟",
 "أيوة ابعته.", "طلب تمديد الحجز {BID} لحد {NCO} اتبعت، وهيوصلك تأكيد من الفندق."],
}

# ───────────────────────── INT010 complaints ─────────────────────────
T['INT010_F1'] = {
'English': ["There is a problem with my room — the air conditioning isn't working.", "I'm sorry about that. Which room are you in?", "Room {ROOM}.",
 "Thank you. I've reported the air conditioning in room {ROOM} to maintenance as a priority. If it can't be fixed quickly, the hotel can offer you another room, subject to availability.",
 "Okay, thanks.", "You're welcome. Reception is available 24/7 if you need anything else."],
'Arabic': ["هناك مشكلة في غرفتي، التكييف لا يعمل.", "نأسف لذلك. في أي غرفة تقيم؟", "الغرفة {ROOM}.",
 "شكراً لك. أبلغت الصيانة بعطل التكييف في الغرفة {ROOM} كأولوية، وإذا تعذر إصلاحه سريعاً يمكن للفندق أن يعرض عليك غرفة أخرى حسب التوافر.",
 "حسناً، شكراً.", "على الرحب والسعة. مكتب الاستقبال متاح على مدار الساعة إذا احتجت أي شيء آخر."],
'French': ["J'ai un problème dans ma chambre : la climatisation ne fonctionne pas.", "Je suis désolé. Dans quelle chambre êtes-vous ?", "Chambre {ROOM}.",
 "Merci. J'ai signalé la climatisation de la chambre {ROOM} à la maintenance en priorité. Si elle ne peut pas être réparée rapidement, l'hôtel peut vous proposer une autre chambre, selon disponibilité.",
 "D'accord, merci.", "Je vous en prie. La réception est disponible 24h/24 si vous avez besoin d'autre chose."],
'Russian': ["У меня проблема в номере: не работает кондиционер.", "Приносим извинения. В каком вы номере?", "Номер {ROOM}.",
 "Спасибо. Я передал неисправность кондиционера в номере {ROOM} в техническую службу как приоритетную. Если быстро починить не получится, отель может предложить другой номер при наличии.",
 "Хорошо, спасибо.", "Пожалуйста. Стойка регистрации работает круглосуточно, если понадобится что-то ещё."],
'Arabic-Egyptian': ["عندي مشكلة في الأوضة، التكييف مش شغال.", "آسفين جداً. انت في أوضة رقم كام؟", "أوضة {ROOM}.",
 "شكراً. بلّغت الصيانة بعطل التكييف في أوضة {ROOM} كأولوية، ولو ماتصلحش بسرعة الفندق يقدر يعرض عليك أوضة تانية على حسب المتاح.",
 "ماشي، شكراً.", "العفو. الاستقبال موجود 24 ساعة لو احتجت أي حاجة تانية."],
}
T['INT010_F2'] = {
'English': ["I want to make a complaint about the service at breakfast this morning.", "I'm sorry to hear that. Could you tell me what happened, and give me your booking reference?",
 "{BID}. We waited forty minutes and nobody came to our table.",
 "Thank you. I've recorded a formal complaint on booking {BID} about the breakfast service. It will be reviewed and the hotel will follow up with you; if you're not satisfied with the outcome, it can be escalated to management.",
 "Thank you.", "You're welcome, and I'm sorry again for the wait."],
'Arabic': ["أريد تقديم شكوى بشأن الخدمة في الإفطار هذا الصباح.", "يؤسفنا سماع ذلك. هل تخبرني بما حدث وتعطيني رقم الحجز؟",
 "{BID}. انتظرنا أربعين دقيقة ولم يأتِ أحد إلى طاولتنا.",
 "شكراً لك. سجلت شكوى رسمية على الحجز {BID} بشأن خدمة الإفطار. ستُراجَع وسيتابع الفندق معك، وإذا لم تكن راضياً عن النتيجة يمكن تصعيدها إلى الإدارة.",
 "شكراً لك.", "على الرحب والسعة، ونعتذر مرة أخرى عن الانتظار."],
'French': ["Je voudrais faire une réclamation sur le service du petit-déjeuner ce matin.", "Je suis désolé de l'apprendre. Pouvez-vous me dire ce qui s'est passé et me donner votre numéro de réservation ?",
 "{BID}. Nous avons attendu quarante minutes et personne n'est venu à notre table.",
 "Merci. J'ai enregistré une réclamation formelle sur la réservation {BID} concernant le service du petit-déjeuner. Elle sera examinée et l'hôtel reviendra vers vous ; si le résultat ne vous convient pas, elle peut être transmise à la direction.",
 "Merci.", "Je vous en prie, et encore désolé pour l'attente."],
'Russian': ["Хочу пожаловаться на обслуживание за завтраком сегодня утром.", "Сожалеем об этом. Расскажите, что произошло, и назовите номер брони.",
 "{BID}. Мы ждали сорок минут, и к нашему столу никто не подошёл.",
 "Спасибо. Я зарегистрировал официальную жалобу по брони {BID} на обслуживание за завтраком. Её рассмотрят, и отель свяжется с вами; если результат вас не устроит, жалобу можно передать руководству.",
 "Спасибо.", "Пожалуйста, и ещё раз извините за ожидание."],
'Arabic-Egyptian': ["عايز أشتكي من الخدمة في الفطار النهارده الصبح.", "آسفين إن ده حصل. قوللي إيه اللي حصل وادّيني رقم الحجز.",
 "{BID}. استنينا أربعين دقيقة ومحدش جه للترابيزة.",
 "شكراً. سجلت شكوى رسمية على الحجز {BID} بخصوص خدمة الفطار، وهتتراجع والفندق هيتابع معاك، ولو مش راضي عن النتيجة ممكن تتصعّد للإدارة.",
 "شكراً.", "العفو، ومتأسفين تاني على الانتظار."],
}
T['INT010_F3'] = {
'English': ["There's a charge on my bill I don't recognise.", "I can log that for review. What is your booking reference?", "{BID}.",
 "Booking {BID} was a {TYPE} from {CI} to {CO}, with a total of {TOTAL} EGP. I've recorded the disputed charge as a billing complaint; customer service will review the transaction and contact you with the outcome.",
 "Thanks.", "You're welcome. Is there anything else I can help with?"],
'Arabic': ["هناك مبلغ في فاتورتي لا أعرف مصدره.", "يمكنني تسجيله للمراجعة. ما رقم الحجز؟", "{BID}.",
 "الحجز {BID} كان {TYPE} من {CI} إلى {CO} بإجمالي {TOTAL} جنيه مصري. سجلت المبلغ محل الاعتراض كشكوى فوترة، وستراجع خدمة العملاء العملية وتتواصل معك بالنتيجة.",
 "شكراً.", "على الرحب والسعة. هل هناك شيء آخر يمكنني مساعدتك فيه؟"],
'French': ["Il y a un montant sur ma facture que je ne reconnais pas.", "Je peux l'enregistrer pour vérification. Quel est votre numéro de réservation ?", "{BID}.",
 "La réservation {BID} était une {TYPE} du {CI} au {CO}, pour un total de {TOTAL} EGP. J'ai enregistré le montant contesté comme réclamation de facturation ; le service clientèle examinera la transaction et vous contactera avec le résultat.",
 "Merci.", "Je vous en prie. Puis-je vous aider pour autre chose ?"],
'Russian': ["В моём счёте есть сумма, которую я не узнаю.", "Могу зарегистрировать это для проверки. Какой номер брони?", "{BID}.",
 "Бронь {BID}: {TYPE}, с {CI} по {CO}, итоговая сумма {TOTAL} EGP. Я зарегистрировал спорную сумму как жалобу по счёту; служба поддержки проверит транзакцию и сообщит вам результат.",
 "Спасибо.", "Пожалуйста. Могу ли я помочь чем-то ещё?"],
'Arabic-Egyptian': ["في مبلغ في الفاتورة مش عارف جه منين.", "أقدر أسجله للمراجعة. رقم الحجز كام؟", "{BID}.",
 "الحجز {BID} كان {TYPE} من {CI} لـ {CO}، وإجماليه {TOTAL} جنيه. سجلت المبلغ اللي معترض عليه كشكوى فاتورة، وخدمة العملاء هتراجع العملية وتكلمك بالنتيجة.",
 "شكراً.", "العفو. في أي حاجة تانية أقدر أساعدك فيها؟"],
}
T['INT010_F4'] = {
'English': ["It's very noisy next to my room and I can't sleep.", "I'm sorry. Which room are you in?", "Room {ROOM}.",
 "Thank you. Reception has been informed about the noise near room {ROOM} and will deal with it now. If it continues, the hotel can look at moving you to another room, subject to availability.",
 "Thank you.", "You're welcome. Reception is available 24/7 if it starts again."],
'Arabic': ["هناك ضوضاء شديدة بجوار غرفتي ولا أستطيع النوم.", "نأسف لذلك. في أي غرفة تقيم؟", "الغرفة {ROOM}.",
 "شكراً لك. أُبلغ مكتب الاستقبال بالضوضاء قرب الغرفة {ROOM} وسيتعامل معها الآن، وإذا استمرت يمكن للفندق النظر في نقلك إلى غرفة أخرى حسب التوافر.",
 "شكراً لك.", "على الرحب والسعة. مكتب الاستقبال متاح على مدار الساعة إذا تكرر الأمر."],
'French': ["Il y a beaucoup de bruit à côté de ma chambre et je n'arrive pas à dormir.", "Je suis désolé. Dans quelle chambre êtes-vous ?", "Chambre {ROOM}.",
 "Merci. La réception a été prévenue du bruit près de la chambre {ROOM} et s'en occupe maintenant. Si cela continue, l'hôtel peut envisager de vous changer de chambre, selon disponibilité.",
 "Merci.", "Je vous en prie. La réception est disponible 24h/24 si cela recommence."],
'Russian': ["Рядом с моим номером очень шумно, я не могу уснуть.", "Сожалеем. В каком вы номере?", "Номер {ROOM}.",
 "Спасибо. Стойку регистрации предупредили о шуме рядом с номером {ROOM}, там сейчас этим займутся. Если шум продолжится, отель может рассмотреть переселение в другой номер при наличии.",
 "Спасибо.", "Пожалуйста. Если шум повторится, стойка регистрации работает круглосуточно."],
'Arabic-Egyptian': ["في دوشة جامدة جنب أوضتي ومش عارف أنام.", "آسفين. انت في أوضة كام؟", "أوضة {ROOM}.",
 "شكراً. الاستقبال اتبلغ بالدوشة اللي جنب أوضة {ROOM} وهيتصرف دلوقتي، ولو استمرت الفندق ممكن يشوفلك أوضة تانية على حسب المتاح.",
 "شكراً.", "العفو. الاستقبال موجود 24 ساعة لو الدوشة رجعت تاني."],
}
T['INT010_F5'] = {
'English': ["I checked out on {CO} but I want to report a problem from my stay.", "Of course. Complaints after checkout are handled by customer service. What is your booking reference?",
 "{BID}. The room wasn't cleaned during my stay.",
 "Thank you. I've recorded a complaint on booking {BID}, a {TYPE} from {CI} to {CO}, about housekeeping. Customer service will review it and follow up with you.",
 "Okay.", "Thank you for letting us know."],
'Arabic': ["غادرت يوم {CO} لكنني أريد الإبلاغ عن مشكلة حدثت أثناء إقامتي.", "بالتأكيد. الشكاوى بعد المغادرة تتولاها خدمة العملاء. ما رقم الحجز؟",
 "{BID}. لم تُنظَّف الغرفة أثناء إقامتي.",
 "شكراً لك. سجلت شكوى على الحجز {BID}، وهو {TYPE} من {CI} إلى {CO}، بشأن تنظيف الغرف. ستراجعها خدمة العملاء وتتابع معك.",
 "حسناً.", "شكراً لإبلاغنا."],
'French': ["J'ai quitté l'hôtel le {CO}, mais je veux signaler un problème survenu pendant mon séjour.", "Bien sûr. Les réclamations après le départ sont traitées par le service clientèle. Quel est votre numéro de réservation ?",
 "{BID}. La chambre n'a pas été nettoyée pendant mon séjour.",
 "Merci. J'ai enregistré une réclamation sur la réservation {BID}, une {TYPE} du {CI} au {CO}, concernant le ménage. Le service clientèle l'examinera et reviendra vers vous.",
 "D'accord.", "Merci de nous l'avoir signalé."],
'Russian': ["Я выехал {CO}, но хочу сообщить о проблеме во время проживания.", "Конечно. Жалобы после выезда рассматривает служба поддержки. Какой номер брони?",
 "{BID}. Во время проживания в номере не убирали.",
 "Спасибо. Я зарегистрировал жалобу по брони {BID} ({TYPE}, с {CI} по {CO}) на уборку. Служба поддержки рассмотрит её и свяжется с вами.",
 "Хорошо.", "Спасибо, что сообщили."],
'Arabic-Egyptian': ["أنا خرجت يوم {CO} بس عايز أبلغ عن مشكلة حصلت وأنا قاعد.", "أكيد. الشكاوى بعد الخروج خدمة العملاء بتتابعها. رقم الحجز كام؟",
 "{BID}. الأوضة ماكانتش بتتنضف طول الإقامة.",
 "شكراً. سجلت شكوى على الحجز {BID}، {TYPE} من {CI} لـ {CO}، بخصوص التنضيف. خدمة العملاء هتراجعها وتتابع معاك.",
 "ماشي.", "شكراً إنك بلغتنا."],
}

# ───────────────────────── INT011 special requests ─────────────────────────
T['INT011_F1'] = {
'English': ["I only eat vegetarian food. Can the hotel cater for that?", "Yes, the hotel can arrange vegetarian meals for breakfast and room service. What is your booking reference, so I can note it?", "{BID}.",
 "Done — a vegetarian meal request is noted on booking {BID} for your stay from {CI} to {CO}. Special requests are confirmed by the hotel.", "Great, thanks.", "You're welcome. Enjoy your stay."],
'Arabic': ["أنا نباتي. هل يمكن للفندق توفير طعام مناسب؟", "نعم، يمكن للفندق ترتيب وجبات نباتية في الإفطار وخدمة الغرف. ما رقم الحجز حتى أسجل ذلك؟", "{BID}.",
 "تم — سُجِّل طلب وجبات نباتية على الحجز {BID} لإقامتك من {CI} إلى {CO}. يؤكد الفندق الطلبات الخاصة.", "ممتاز، شكراً.", "على الرحب والسعة. نتمنى لك إقامة سعيدة."],
'French': ["Je suis végétarien. L'hôtel peut-il s'adapter ?", "Oui, l'hôtel peut prévoir des repas végétariens au petit-déjeuner et au room service. Quel est votre numéro de réservation, pour que je le note ?", "{BID}.",
 "C'est fait — une demande de repas végétariens est notée sur la réservation {BID} pour votre séjour du {CI} au {CO}. Les demandes spéciales sont confirmées par l'hôtel.", "Parfait, merci.", "Je vous en prie. Bon séjour."],
'Russian': ["Я вегетарианец. Отель может это учесть?", "Да, отель может организовать вегетарианское питание на завтраке и в обслуживании номеров. Назовите номер брони, чтобы я это отметил.", "{BID}.",
 "Готово — запрос на вегетарианское питание отмечен в брони {BID} на период с {CI} по {CO}. Особые пожелания подтверждает отель.", "Отлично, спасибо.", "Пожалуйста. Приятного пребывания."],
'Arabic-Egyptian': ["أنا نباتي. الفندق يقدر يوفرلي أكل مناسب؟", "أيوة، الفندق يقدر يرتبلك أكل نباتي في الفطار وخدمة الأوض. رقم الحجز كام عشان أسجله؟", "{BID}.",
 "تمام، طلب الأكل النباتي اتسجل على الحجز {BID} لإقامتك من {CI} لـ {CO}، والفندق هو اللي بيأكد الطلبات الخاصة.", "حلو، شكراً.", "العفو. إقامة سعيدة."],
}
T['INT011_F2'] = {
'English': ["Could I have a quiet room away from the lifts?", "I can add that as a preference. What is your booking reference?", "{BID}.",
 "Noted on booking {BID} ({CI} to {CO}): a quiet room away from the elevators. Preferences depend on availability when rooms are allocated, and the hotel will confirm.", "Thank you.", "You're welcome."],
'Arabic': ["هل يمكن أن أحصل على غرفة هادئة بعيداً عن المصاعد؟", "يمكنني إضافة ذلك كتفضيل. ما رقم الحجز؟", "{BID}.",
 "سُجِّل على الحجز {BID} (من {CI} إلى {CO}): غرفة هادئة بعيداً عن المصاعد. التفضيلات تعتمد على التوافر عند تخصيص الغرف، وسيؤكد الفندق ذلك.", "شكراً لك.", "على الرحب والسعة."],
'French': ["Pourrais-je avoir une chambre calme, loin des ascenseurs ?", "Je peux l'ajouter comme préférence. Quel est votre numéro de réservation ?", "{BID}.",
 "C'est noté sur la réservation {BID} (du {CI} au {CO}) : une chambre calme loin des ascenseurs. Les préférences dépendent de la disponibilité lors de l'attribution des chambres, et l'hôtel confirmera.", "Merci.", "Je vous en prie."],
'Russian': ["Можно тихий номер подальше от лифтов?", "Могу добавить это как пожелание. Какой номер брони?", "{BID}.",
 "Отмечено в брони {BID} (с {CI} по {CO}): тихий номер подальше от лифтов. Пожелания зависят от наличия при распределении номеров, отель подтвердит.", "Спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["ينفع آخد أوضة هادية بعيد عن الأسانسير؟", "أقدر أضيفها كطلب. رقم الحجز كام؟", "{BID}.",
 "اتسجل على الحجز {BID} (من {CI} لـ {CO}): أوضة هادية بعيد عن الأسانسير. ده على حسب المتاح وقت توزيع الأوض، والفندق هيأكد.", "شكراً.", "العفو."],
}
T['INT011_F3'] = {
'English': ["We're celebrating our anniversary during our stay. Can you arrange something?", "Congratulations! The hotel can arrange room decoration and special set-ups on request; some arrangements may carry an extra charge. What is your booking reference?", "{BID}.",
 "I've added an anniversary request to booking {BID} for your stay starting {CI}. The hotel will contact you to confirm what can be arranged and any cost.", "Wonderful, thanks.", "You're welcome."],
'Arabic': ["نحتفل بذكرى زواجنا أثناء إقامتنا. هل يمكنكم ترتيب شيء ما؟", "مبروك! يمكن للفندق ترتيب تزيين الغرفة وتجهيزات خاصة عند الطلب، وقد تترتب رسوم إضافية على بعض الترتيبات. ما رقم الحجز؟", "{BID}.",
 "أضفت طلب الاحتفال بذكرى الزواج إلى الحجز {BID} لإقامتك التي تبدأ يوم {CI}. سيتواصل معك الفندق لتأكيد ما يمكن ترتيبه وأي تكلفة.", "رائع، شكراً.", "على الرحب والسعة."],
'French': ["Nous fêtons notre anniversaire de mariage pendant le séjour. Pouvez-vous organiser quelque chose ?", "Félicitations ! L'hôtel peut organiser une décoration de chambre et des installations spéciales sur demande ; certains arrangements peuvent entraîner un supplément. Quel est votre numéro de réservation ?", "{BID}.",
 "J'ai ajouté une demande d'anniversaire à la réservation {BID} pour votre séjour à partir du {CI}. L'hôtel vous contactera pour confirmer ce qui peut être organisé et le coût éventuel.", "Merveilleux, merci.", "Je vous en prie."],
'Russian': ["Во время проживания у нас годовщина свадьбы. Можете что-нибудь организовать?", "Поздравляем! Отель может украсить номер и подготовить особое оформление по запросу; за некоторые услуги возможна доплата. Какой номер брони?", "{BID}.",
 "Я добавил запрос на празднование годовщины в бронь {BID} с датой заезда {CI}. Отель свяжется с вами, чтобы подтвердить, что можно организовать и сколько это стоит.", "Замечательно, спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["عندنا عيد جواز وإحنا في الفندق. تقدروا ترتبولنا حاجة؟", "مبروك! الفندق يقدر يزيّن الأوضة ويعمل ترتيبات خاصة عند الطلب، وبعض الترتيبات ممكن يبقى عليها رسوم. رقم الحجز كام؟", "{BID}.",
 "ضفت طلب الاحتفال بعيد الجواز على الحجز {BID} لإقامتك اللي بتبدأ يوم {CI}. الفندق هيكلمك يأكدلك إيه اللي ينفع يترتب وتكلفته.", "جميل، شكراً.", "العفو."],
}
T['INT011_F4'] = {
'English': ["Can we add an extra bed for our child?", "Let me check your booking. What is the reference?", "{BID}.",
 {'fit': "Booking {BID} is a {TYPE} from {CI} to {CO} for {G} guests. It holds up to {CAP}, children included, so one more guest fits. An extra bed is 2,500 EGP per night, subject to availability. Shall I request it?",
  'over': "Booking {BID} is a {TYPE} from {CI} to {CO} for {G} guests. It holds up to {CAP}, children included, so a child would exceed its capacity even with an extra bed. A {ALT} holds up to {ALTCAP} guests at a standard rate of {ALTBASE} EGP per night. Shall I request a change to a {ALT}, subject to availability?"},
 "Yes, please.",
 {'fit': "Requested — an extra bed has been added to booking {BID}, and the hotel will confirm.",
  'over': "Requested — the change of {BID} to a {ALT} has been submitted, subject to availability and hotel approval."}],
'Arabic': ["هل يمكن إضافة سرير إضافي لطفلنا؟", "دعني أتحقق من حجزك. ما رقم الحجز؟", "{BID}.",
 {'fit': "الحجز {BID} هو {TYPE} من {CI} إلى {CO}، وعدد النزلاء {G}، وسعتها القصوى {CAP} بمن فيهم الأطفال، فنزيل إضافي مناسب. السرير الإضافي بسعر 2,500 جنيه مصري لليلة حسب التوافر. هل أطلبه؟",
  'over': "الحجز {BID} هو {TYPE} من {CI} إلى {CO}، وعدد النزلاء {G}، وسعتها القصوى {CAP} بمن فيهم الأطفال، لذا فإن إضافة طفل تتجاوز سعتها حتى مع سرير إضافي. {ALT} بسعة قصوى {ALTCAP} وبسعر قياسي {ALTBASE} جنيه مصري لليلة. هل أطلب التغيير إلى {ALT} حسب التوافر؟"},
 "نعم، من فضلك.",
 {'fit': "تم الطلب — أُضيف سرير إضافي إلى الحجز {BID}، وسيؤكده الفندق.",
  'over': "تم الطلب — أُرسل طلب تغيير الحجز {BID} إلى {ALT} حسب التوافر وموافقة الفندق."}],
'French': ["Peut-on ajouter un lit supplémentaire pour notre enfant ?", "Je vérifie votre réservation. Quel est le numéro ?", "{BID}.",
 {'fit': "La réservation {BID} est une {TYPE} du {CI} au {CO} pour {G} personnes. Elle accueille jusqu'à {CAP} personnes, enfants compris, donc une personne de plus y tient. Un lit supplémentaire coûte 2 500 EGP par nuit, selon disponibilité. Dois-je le demander ?",
  'over': "La réservation {BID} est une {TYPE} du {CI} au {CO} pour {G} personnes. Elle accueille jusqu'à {CAP} personnes, enfants compris, donc un enfant de plus dépasserait sa capacité, même avec un lit supplémentaire. Une {ALT} accueille jusqu'à {ALTCAP} personnes au tarif standard de {ALTBASE} EGP par nuit. Dois-je demander le passage en {ALT}, sous réserve de disponibilité ?"},
 "Oui, s'il vous plaît.",
 {'fit': "C'est demandé — un lit supplémentaire a été ajouté à la réservation {BID}, et l'hôtel confirmera.",
  'over': "C'est demandé — le passage de {BID} en {ALT} a été envoyé, sous réserve de disponibilité et d'accord de l'hôtel."}],
'Russian': ["Можно добавить дополнительную кровать для ребёнка?", "Проверю вашу бронь. Какой номер?", "{BID}.",
 {'fit': "Бронь {BID}: {TYPE}, с {CI} по {CO}, гостей — {G}. Вместимость номера — {CAP}, включая детей, так что ещё один гость помещается. Дополнительная кровать стоит 2 500 EGP за ночь при наличии. Запросить её?",
  'over': "Бронь {BID}: {TYPE}, с {CI} по {CO}, гостей — {G}. Вместимость номера — {CAP}, включая детей, поэтому ребёнок превысит её даже с дополнительной кроватью. {ALT} вмещает до {ALTCAP} гостей, стандартный тариф {ALTBASE} EGP за ночь. Запросить смену на {ALT} при наличии мест?"},
 "Да, пожалуйста.",
 {'fit': "Запрошено — дополнительная кровать добавлена в бронь {BID}, отель подтвердит.",
  'over': "Запрошено — смена брони {BID} на {ALT} отправлена, при наличии мест и с одобрения отеля."}],
'Arabic-Egyptian': ["ينفع نزود سرير إضافي لابننا؟", "ثانية أشوف الحجز. رقمه كام؟", "{BID}.",
 {'fit': "الحجز {BID} {TYPE} من {CI} لـ {CO}، وعدد الأفراد {G}، وبتاخد لحد {CAP} والأطفال محسوبين، يعني فرد زيادة ينفع. السرير الإضافي بـ 2,500 جنيه في الليلة على حسب المتاح. أطلبهولك؟",
  'over': "الحجز {BID} {TYPE} من {CI} لـ {CO}، وعدد الأفراد {G}، وبتاخد لحد {CAP} بس والأطفال محسوبين، يعني طفل زيادة هيعدّي السعة حتى بسرير إضافي. {ALT} بتاخد لحد {ALTCAP} وسعرها الأساسي {ALTBASE} جنيه في الليلة. أطلبلك تغيير لـ {ALT} على حسب المتاح؟"},
 "أيوة لو سمحت.",
 {'fit': "تمام، السرير الإضافي اتضاف على الحجز {BID} والفندق هيأكد.",
  'over': "تمام، طلب تغيير الحجز {BID} لـ {ALT} اتبعت، على حسب المتاح وموافقة الفندق."}],
}
T['INT011_F5'] = {
'English': ["My flight lands very late — I'll arrive after midnight.", "Thanks for letting us know. What is your booking reference?", "{BID}.",
 "Booking {BID} starts on {CI}. A reservation is held until 23:59 on the arrival date, so I've added a late-arrival note to it — that way it won't be recorded as a no-show. Reception is open 24/7 and can check you in at any hour.",
 "Perfect, thank you.", "You're welcome. Safe travels."],
'Arabic': ["رحلتي تصل متأخرة جداً، وسأصل بعد منتصف الليل.", "شكراً لإبلاغنا. ما رقم الحجز؟", "{BID}.",
 "الحجز {BID} يبدأ يوم {CI}. يُحتفظ بالحجز حتى الساعة 23:59 من يوم الوصول، لذا أضفت إليه ملاحظة بالوصول المتأخر حتى لا يُسجَّل كعدم حضور. مكتب الاستقبال يعمل على مدار الساعة ويمكنه إتمام تسجيل وصولك في أي وقت.",
 "ممتاز، شكراً لك.", "على الرحب والسعة. رحلة آمنة."],
'French': ["Mon vol arrive très tard — j'arriverai après minuit.", "Merci de nous prévenir. Quel est votre numéro de réservation ?", "{BID}.",
 "La réservation {BID} commence le {CI}. Une réservation est maintenue jusqu'à 23h59 le jour de l'arrivée, j'y ai donc ajouté une note d'arrivée tardive — ainsi elle ne sera pas enregistrée comme non-présentation. La réception est ouverte 24h/24 et peut vous enregistrer à toute heure.",
 "Parfait, merci.", "Je vous en prie. Bon voyage."],
'Russian': ["Мой рейс прилетает очень поздно — я приеду после полуночи.", "Спасибо, что предупредили. Какой номер брони?", "{BID}.",
 "Бронь {BID} начинается {CI}. Бронь сохраняется до 23:59 в день заезда, поэтому я добавил отметку о позднем прибытии — так она не будет зафиксирована как неявка. Стойка регистрации работает круглосуточно и заселит вас в любое время.",
 "Отлично, спасибо.", "Пожалуйста. Хорошей дороги."],
'Arabic-Egyptian': ["طيارتي هتوصل متأخر أوي، وهوصل بعد نص الليل.", "شكراً إنك بلغتنا. رقم الحجز كام؟", "{BID}.",
 "الحجز {BID} بيبدأ يوم {CI}. الحجز بيفضل محجوز لحد 11:59 بالليل يوم الوصول، فضفت عليه ملاحظة إنك هتوصل متأخر عشان مايتسجلش عدم حضور. الاستقبال شغال 24 ساعة ويقدر يعملك check-in في أي وقت.",
 "تمام، شكراً.", "العفو. توصل بالسلامة."],
}

# ───────────────────────── INT012 loyalty ─────────────────────────
OPENERS['INT012_F1'] = {
 'English': ["Does the hotel have a loyalty programme?", "Is there a membership programme for regular guests?", "I stay here often — is there a rewards scheme?"],
 'Arabic': ["هل لدى الفندق برنامج ولاء؟", "هل يوجد برنامج عضوية للضيوف الدائمين؟", "أقيم عندكم كثيراً، هل هناك برنامج مكافآت؟"],
 'French': ["L'hôtel a-t-il un programme de fidélité ?", "Existe-t-il un programme d'adhésion pour les clients réguliers ?", "Je séjourne souvent chez vous — y a-t-il un programme de récompenses ?"],
 'Russian': ["Есть ли в отеле программа лояльности?", "Есть ли программа для постоянных гостей?", "Я часто у вас останавливаюсь — есть ли бонусная программа?"],
 'Arabic-Egyptian': ["عندكم برنامج ولاء؟", "في عضوية للزباين الدايمين؟", "أنا بنزل عندكم كتير، في برنامج مكافآت؟"]}
T['INT012_F1'] = {
'English': [None, "Yes — Nile Pearl Rewards is free to join. Members earn points on every stay, get the Loyalty Member rate of 15% off and, from Silver level, late check-out and upgrades.",
 "How do I join?", "You can enrol during booking or at check-in, and membership may also be available through the hotel website.", "Thanks.", "You're welcome. Is there anything else I can help with?"],
'Arabic': [None, "نعم، برنامج Nile Pearl Rewards مجاني، ويكسب الأعضاء نقاطاً على كل إقامة ويحصلون على سعر الأعضاء بخصم 15%، ومن المستوى الفضي يحصلون على مغادرة متأخرة وترقيات.",
 "كيف أشترك؟", "يمكنك الاشتراك عند الحجز أو عند تسجيل الوصول، وقد يتاح الاشتراك أيضاً عبر موقع الفندق.", "شكراً.", "على الرحب والسعة. هل هناك شيء آخر يمكنني مساعدتك فيه؟"],
'French': [None, "Oui — l'adhésion à Nile Pearl Rewards est gratuite. Les membres gagnent des points à chaque séjour, profitent du tarif membre à -15 % et, dès le niveau Silver, d'un départ tardif et de surclassements.",
 "Comment m'inscrire ?", "Vous pouvez vous inscrire lors de la réservation ou à l'arrivée, et l'adhésion peut aussi être possible sur le site de l'hôtel.", "Merci.", "Je vous en prie. Puis-je vous aider pour autre chose ?"],
'Russian': [None, "Да — вступить в Nile Pearl Rewards можно бесплатно. Участники получают баллы за каждое проживание, тариф участника со скидкой 15 %, а с уровня Silver — поздний выезд и повышение категории.",
 "Как вступить?", "Вступить можно при бронировании или при заселении, а также, возможно, через сайт отеля.", "Спасибо.", "Пожалуйста. Могу ли я помочь чем-то ещё?"],
'Arabic-Egyptian': [None, "أيوة، برنامج Nile Pearl Rewards ببلاش، وبتاخد نقط على كل إقامة وسعر الأعضاء بخصم 15%، ومن المستوى الفضي بتاخد خروج متأخر وترقيات.",
 "أشترك إزاي؟", "تقدر تشترك وقت الحجز أو وقت الدخول، وممكن كمان من موقع الفندق.", "شكراً.", "العفو. في حاجة تانية أقدر أساعدك فيها؟"],
}
OPENERS['INT012_F2'] = {
 'English': ["How do I earn points at this hotel?", "Do my bookings earn any points?", "I want to understand the points system."],
 'Arabic': ["كيف أكسب النقاط في هذا الفندق؟", "هل تكسب حجوزاتي أي نقاط؟", "أريد أن أفهم نظام النقاط."],
 'French': ["Comment gagner des points dans cet hôtel ?", "Mes réservations rapportent-elles des points ?", "Je voudrais comprendre le système de points."],
 'Russian': ["Как получать баллы в этом отеле?", "Начисляются ли баллы за мои бронирования?", "Хочу разобраться в системе баллов."],
 'Arabic-Egyptian': ["باخد نقط إزاي عندكم؟", "الحجوزات بتاعتي بتجيب نقط؟", "عايز أفهم نظام النقط."]}
T['INT012_F2'] = {
'English': [None, "Members earn 1 point for every ten Egyptian pounds spent on rooms and services, plus a tier bonus: Silver +20%, Gold +50%, Platinum +100%.", "And what can I use them for?",
 "Every 1,000 points give a 500 EGP discount on rooms or services. Points expire after 24 months without activity and cannot be transferred.", "Thanks.", "You're welcome."],
'Arabic': [None, "يكسب الأعضاء نقطة عن كل عشرة جنيهات تُنفق على الغرف والخدمات، مع مكافأة المستوى: الفضي 20% والذهبي 50% والبلاتيني 100%.", "وفيمَ أستخدمها؟",
 "كل 1,000 نقطة تمنحك خصم 500 جنيه مصري على الغرف أو الخدمات، وتنتهي صلاحية النقاط بعد 24 شهراً دون نشاط ولا يمكن نقلها.", "شكراً.", "على الرحب والسعة."],
'French': [None, "Les membres gagnent 1 point par tranche de dix livres égyptiennes dépensées en chambres et services, plus un bonus de niveau : Silver +20 %, Gold +50 %, Platinum +100 %.", "Et à quoi puis-je les utiliser ?",
 "1 000 points donnent une remise de 500 EGP sur les chambres ou les services. Les points expirent après 24 mois sans activité et ne sont pas transférables.", "Merci.", "Je vous en prie."],
'Russian': [None, "Участники получают 1 балл за каждые десять египетских фунтов, потраченных на номера и услуги, плюс бонус уровня: Silver +20 %, Gold +50 %, Platinum +100 %.", "А на что их можно потратить?",
 "1 000 баллов дают скидку 500 EGP на номера или услуги. Баллы сгорают после 24 месяцев без активности и не передаются.", "Спасибо.", "Пожалуйста."],
'Arabic-Egyptian': [None, "الأعضاء بياخدوا نقطة على كل عشرة جنيه بيصرفوها على الأوض والخدمات، وفوقها بونص: الفضي 20% والدهبي 50% والبلاتيني 100%.", "وأستخدمها في إيه؟",
 "كل 1,000 نقطة بخصم 500 جنيه على الأوض أو الخدمات، والنقط بتخلص بعد 24 شهر من غير نشاط ومينفعش تتنقل.", "شكراً.", "العفو."],
}
OPENERS['INT012_F3'] = {
 'English': ["What membership levels are there?", "Are there different tiers in the programme?", "How is the membership structured?"],
 'Arabic': ["ما مستويات العضوية المتاحة؟", "هل توجد مستويات مختلفة في البرنامج؟", "كيف تُقسَّم العضوية؟"],
 'French': ["Quels sont les niveaux d'adhésion ?", "Y a-t-il différents niveaux dans le programme ?", "Comment l'adhésion est-elle structurée ?"],
 'Russian': ["Какие уровни членства существуют?", "Есть ли в программе разные уровни?", "Как устроено членство?"],
 'Arabic-Egyptian': ["إيه مستويات العضوية؟", "في مستويات مختلفة في البرنامج؟", "العضوية مقسمة إزاي؟"]}
T['INT012_F3'] = {
'English': [None, "There are four tiers: Standard on joining, Silver at 10 nights, Gold at 25 nights and Platinum at 50 nights in a calendar year.", "What do members get?",
 "Silver: late check-out until 1:00 PM. Gold: until 2:00 PM, a room upgrade and 10% off the spa. Platinum: until 4:00 PM, free breakfast for two, priority upgrades and 15% off the spa — subject to availability.", "Thanks.", "You're welcome."],
'Arabic': [None, "هناك أربعة مستويات: العادي عند الانضمام، والفضي بعد 10 ليالٍ، والذهبي بعد 25 ليلة، والبلاتيني بعد 50 ليلة في السنة الميلادية.", "وما الذي يحصل عليه الأعضاء؟",
 "الفضي: مغادرة متأخرة حتى 1:00 ظهراً. الذهبي: حتى 2:00 ظهراً مع ترقية للغرفة وخصم 10% في السبا. البلاتيني: حتى 4:00 عصراً مع إفطار مجاني لشخصين وأولوية في الترقية وخصم 15% في السبا، وكل ذلك حسب التوافر.", "شكراً.", "على الرحب والسعة."],
'French': [None, "Il y a quatre niveaux : Standard à l'inscription, Silver à 10 nuits, Gold à 25 nuits et Platinum à 50 nuits par année civile.", "Qu'obtiennent les membres ?",
 "Silver : départ tardif jusqu'à 13h00. Gold : jusqu'à 14h00, un surclassement et -10 % au spa. Platinum : jusqu'à 16h00, petit-déjeuner offert pour deux, surclassements prioritaires et -15 % au spa — selon disponibilité.", "Merci.", "Je vous en prie."],
'Russian': [None, "Уровней четыре: Standard при вступлении, Silver за 10 ночей, Gold за 25 ночей и Platinum за 50 ночей в календарном году.", "Что получают участники?",
 "Silver: поздний выезд до 13:00. Gold: до 14:00, повышение категории и −10 % в спа. Platinum: до 16:00, бесплатный завтрак на двоих, приоритетное повышение и −15 % в спа — при наличии.", "Спасибо.", "Пожалуйста."],
'Arabic-Egyptian': [None, "في 4 مستويات: العادي أول ما تشترك، والفضي بعد 10 ليالي، والدهبي بعد 25، والبلاتيني بعد 50 ليلة في السنة.", "والأعضاء بياخدوا إيه؟",
 "الفضي: خروج لحد 1 الضهر. الدهبي: لحد 2 الضهر وترقية للأوضة وخصم 10% في السبا. البلاتيني: لحد 4 العصر وفطار ببلاش لاتنين وأولوية في الترقية وخصم 15% في السبا، وكله على حسب المتاح.", "شكراً.", "العفو."],
}
T['INT012_F4'] = {
'English': ["I'm a loyalty member. Could I get an upgrade on my next stay?", "Let me check. What is your booking reference?", "{BID}.",
 {'mem': "Booking {BID} ({TYPE}, {CI} to {CO}) is linked to a {TIER} membership. Members may be eligible for a complimentary upgrade, subject to availability at check-in. I've added an upgrade request to the booking, and the hotel will confirm.",
  'non': "I couldn't find a loyalty membership on the account holding booking {BID} ({TYPE}, {CI} to {CO}). You can join during booking, at check-in or through the hotel website, and members may be offered upgrades subject to availability."},
 "Okay, thanks.", "You're welcome."],
'Arabic': ["أنا عضو في برنامج الولاء. هل يمكنني الحصول على ترقية في إقامتي القادمة؟", "دعني أتحقق. ما رقم الحجز؟", "{BID}.",
 {'mem': "الحجز {BID} ({TYPE}، من {CI} إلى {CO}) مرتبط بعضوية من المستوى {TIER}. قد يكون الأعضاء مؤهلين لترقية مجانية حسب التوافر عند تسجيل الوصول. أضفت طلب ترقية إلى الحجز وسيؤكده الفندق.",
  'non': "لم أجد عضوية ولاء على الحساب صاحب الحجز {BID} ({TYPE}، من {CI} إلى {CO}). يمكنك الاشتراك عند الحجز أو عند تسجيل الوصول أو عبر موقع الفندق، وقد تُعرض على الأعضاء ترقيات حسب التوافر."},
 "حسناً، شكراً.", "على الرحب والسعة."],
'French': ["Je suis membre du programme de fidélité. Puis-je avoir un surclassement lors de mon prochain séjour ?", "Je vérifie. Quel est votre numéro de réservation ?", "{BID}.",
 {'mem': "La réservation {BID} ({TYPE}, du {CI} au {CO}) est liée à une adhésion de niveau {TIER}. Les membres peuvent bénéficier d'un surclassement offert, selon disponibilité à l'arrivée. J'ai ajouté une demande de surclassement à la réservation, et l'hôtel confirmera.",
  'non': "Je n'ai pas trouvé d'adhésion au programme de fidélité sur le compte de la réservation {BID} ({TYPE}, du {CI} au {CO}). Vous pouvez adhérer lors de la réservation, à l'arrivée ou sur le site de l'hôtel, et les membres peuvent se voir proposer des surclassements selon disponibilité."},
 "D'accord, merci.", "Je vous en prie."],
'Russian': ["Я участник программы лояльности. Можно получить повышение категории в следующий приезд?", "Сейчас проверю. Какой номер брони?", "{BID}.",
 {'mem': "Бронь {BID} ({TYPE}, с {CI} по {CO}) связана с членством уровня {TIER}. Участники могут получить бесплатное повышение категории при наличии на момент заселения. Я добавил запрос на повышение в бронь, отель подтвердит.",
  'non': "На аккаунте брони {BID} ({TYPE}, с {CI} по {CO}) я не нашёл членства в программе лояльности. Вступить можно при бронировании, при заселении или через сайт отеля, а участникам могут предлагать повышение категории при наличии."},
 "Хорошо, спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["أنا عضو في برنامج الولاء. ينفع آخد ترقية في الإقامة الجاية؟", "ثانية أشوف. رقم الحجز كام؟", "{BID}.",
 {'mem': "الحجز {BID} ({TYPE}، من {CI} لـ {CO}) مربوط بعضوية المستوى {TIER}. الأعضاء ممكن ياخدوا ترقية مجانية على حسب المتاح وقت الدخول. ضفت طلب ترقية على الحجز والفندق هيأكد.",
  'non': "مالقيتش عضوية ولاء على الحساب اللي عليه الحجز {BID} ({TYPE}، من {CI} لـ {CO}). تقدر تشترك وقت الحجز أو وقت الدخول أو من موقع الفندق، والأعضاء ممكن ياخدوا ترقيات على حسب المتاح."},
 "ماشي، شكراً.", "العفو."],
}
T['INT012_F5'] = {
'English': ["How many loyalty points do I have?", "I can check. What is your membership number?", "{MID}.",
 "Membership {MID} is at {TIER} level, with {POINTS} points and {STAYS} stays recorded. Points can be redeemed for discounts, free nights or hotel services.", "Great, thanks.", "You're welcome."],
'Arabic': ["كم نقطة ولاء لديّ؟", "يمكنني التحقق. ما رقم العضوية؟", "{MID}.",
 "العضوية {MID} في المستوى {TIER}، ورصيدها {POINTS} نقطة، وعدد الإقامات المسجلة {STAYS}. يمكن استبدال النقاط بخصومات أو ليالٍ مجانية أو خدمات فندقية.", "ممتاز، شكراً.", "على الرحب والسعة."],
'French': ["Combien de points de fidélité ai-je ?", "Je peux vérifier. Quel est votre numéro de membre ?", "{MID}.",
 "L'adhésion {MID} est au niveau {TIER}, avec un solde de {POINTS} points et {STAYS} séjours enregistrés. Les points s'échangent contre des réductions, des nuits offertes ou des services de l'hôtel.", "Parfait, merci.", "Je vous en prie."],
'Russian': ["Сколько у меня баллов лояльности?", "Могу проверить. Какой у вас номер участника?", "{MID}.",
 "Участник {MID}: уровень {TIER}, баланс баллов — {POINTS}, зарегистрированных проживаний — {STAYS}. Баллы можно обменять на скидки, бесплатные ночи или услуги отеля.", "Отлично, спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["عندي كام نقطة ولاء؟", "أقدر أشوفلك. رقم العضوية كام؟", "{MID}.",
 "العضوية {MID} في المستوى {TIER}، ورصيدك {POINTS} نقطة، وعدد الإقامات المسجلة {STAYS}. النقط تتبدل بخصومات أو ليالي مجانية أو خدمات في الفندق.", "حلو، شكراً.", "العفو."],
}

# ───────────────────────── INT013 facilities ─────────────────────────
FAC = {
 'English': "The hotel has a swimming pool, a gym, free Wi-Fi, parking, 24/7 reception, room service, a main restaurant and a spa; airport transfer is available on request.",
 'Arabic': "يوفر الفندق حمام سباحة وصالة رياضية وإنترنت مجانياً ومواقف سيارات واستقبالاً على مدار الساعة وخدمة غرف ومطعماً رئيسياً وسبا، وخدمة النقل من المطار متاحة عند الطلب.",
 'French': "L'hôtel dispose d'une piscine, d'une salle de sport, du Wi-Fi gratuit, d'un parking, d'une réception 24h/24, d'un room service, d'un restaurant principal et d'un spa ; le transfert aéroport est disponible sur demande.",
 'Russian': "В отеле есть бассейн, тренажёрный зал, бесплатный Wi-Fi, парковка, круглосуточная стойка регистрации, обслуживание номеров, основной ресторан и спа; трансфер из аэропорта — по запросу.",
 'Arabic-Egyptian': "الفندق فيه حمام سباحة وجيم وواي فاي مجاني وجراج واستقبال 24 ساعة وخدمة غرف ومطعم رئيسي وسبا، والتوصيل من المطار متاح عند الطلب."}
CLOSE = {'English': ("Thanks.", "You're welcome."), 'Arabic': ("شكراً.", "على الرحب والسعة."), 'French': ("Merci.", "Je vous en prie."),
         'Russian': ("Спасибо.", "Пожалуйста."), 'Arabic-Egyptian': ("شكراً.", "العفو.")}
OPENERS['INT013_F1'] = {
 'English': ["What facilities does the hotel have?", "What can guests use during their stay?", "Can you tell me what is available at the hotel?"],
 'Arabic': ["ما المرافق المتوفرة في الفندق؟", "ما الذي يمكن للنزلاء استخدامه أثناء الإقامة؟", "هل تخبرني بما هو متاح في الفندق؟"],
 'French': ["Quels équipements l'hôtel propose-t-il ?", "De quoi les clients peuvent-ils profiter pendant leur séjour ?", "Pouvez-vous me dire ce qui est disponible à l'hôtel ?"],
 'Russian': ["Какие удобства есть в отеле?", "Чем могут пользоваться гости во время проживания?", "Расскажите, что есть в отеле?"],
 'Arabic-Egyptian': ["الفندق فيه إيه من المرافق؟", "النزلاء يقدروا يستخدموا إيه وهما قاعدين؟", "ممكن تقولي إيه المتاح في الفندق؟"]}
POOL_Q = {'English': "What are the pool hours?", 'Arabic': "ما مواعيد حمام السباحة؟", 'French': "Quels sont les horaires de la piscine ?", 'Russian': "Какие часы работы бассейна?", 'Arabic-Egyptian': "حمام السباحة مواعيده إيه؟"}
POOL_A = {'English': "The swimming pool is open to hotel guests from 7:00 AM to 9:00 PM.", 'Arabic': "حمام السباحة متاح لنزلاء الفندق من الساعة 7:00 صباحاً حتى 9:00 مساءً.",
 'French': "La piscine est ouverte aux clients de 7h00 à 21h00.", 'Russian': "Бассейн открыт для гостей отеля с 7:00 до 21:00.", 'Arabic-Egyptian': "حمام السباحة مفتوح للنزلاء من 7 الصبح لحد 9 بالليل."}
T['INT013_F1'] = {l: [None, FAC[l], POOL_Q[l], POOL_A[l], CLOSE[l][0], CLOSE[l][1]] for l in L}
OPENERS['INT013_F2'] = {
 'English': ["Is there a gym in the hotel?", "Do you have exercise facilities?", "I would like to use a fitness centre."],
 'Arabic': ["هل توجد صالة رياضية في الفندق؟", "هل لديكم مرافق للتمارين؟", "أود استخدام مركز لياقة بدنية."],
 'French': ["Y a-t-il une salle de sport à l'hôtel ?", "Avez-vous des équipements pour faire de l'exercice ?", "J'aimerais utiliser une salle de fitness."],
 'Russian': ["Есть ли в отеле тренажёрный зал?", "У вас есть где позаниматься спортом?", "Я хотел бы пользоваться фитнес-центром."],
 'Arabic-Egyptian': ["في جيم في الفندق؟", "عندكم مكان للتمارين؟", "عايز أستخدم الجيم."]}
T['INT013_F2'] = {
'English': [None, "Yes, the gym is open 24/7 and free for hotel guests, with cardio machines and free weights.", "Do I have to pay for Wi-Fi?", "No, Wi-Fi is free and available 24/7 in all rooms and public areas.", "Thanks.", "You're welcome."],
'Arabic': [None, "نعم، الصالة الرياضية مفتوحة على مدار الساعة ومجانية لنزلاء الفندق، وبها أجهزة كارديو وأوزان حرة.", "هل الإنترنت اللاسلكي مدفوع؟", "لا، الإنترنت اللاسلكي مجاني ومتاح على مدار الساعة في جميع الغرف والمناطق العامة.", "شكراً.", "على الرحب والسعة."],
'French': [None, "Oui, la salle de sport est ouverte 24h/24 et gratuite pour les clients, avec appareils cardio et poids libres.", "Le Wi-Fi est-il payant ?", "Non, le Wi-Fi est gratuit et disponible 24h/24 dans toutes les chambres et les espaces communs.", "Merci.", "Je vous en prie."],
'Russian': [None, "Да, тренажёрный зал работает круглосуточно и бесплатен для гостей: кардиотренажёры и свободные веса.", "Wi-Fi платный?", "Нет, Wi-Fi бесплатный и доступен круглосуточно во всех номерах и общественных зонах.", "Спасибо.", "Пожалуйста."],
'Arabic-Egyptian': [None, "أيوة، الجيم مفتوح 24 ساعة ومجاني للنزلاء، وفيه أجهزة كارديو وأوزان.", "الواي فاي بفلوس؟", "لأ، الواي فاي مجاني وشغال 24 ساعة في كل الأوض والأماكن العامة.", "شكراً.", "العفو."],
}
T['INT013_F3'] = {
'English': ["What time is breakfast served?", "Breakfast is served in the main restaurant from 7:00 AM to 10:30 AM, at 1,200 EGP per adult.", "I'll need a vegetarian option — booking {BID}.",
 "Noted — a vegetarian breakfast request is on booking {BID} for your stay from {CI}. The hotel will confirm.", "Thanks.", "You're welcome."],
'Arabic': ["في أي ساعة يُقدَّم الإفطار؟", "يُقدَّم الإفطار في المطعم الرئيسي من 7:00 حتى 10:30 صباحاً بسعر 1,200 جنيه مصري للبالغ.", "سأحتاج إلى خيار نباتي، والحجز رقم {BID}.",
 "تم التسجيل — طلب إفطار نباتي مضاف إلى الحجز {BID} لإقامتك التي تبدأ يوم {CI}، وسيؤكده الفندق.", "شكراً.", "على الرحب والسعة."],
'French': ["À quelle heure est servi le petit-déjeuner ?", "Le petit-déjeuner est servi au restaurant principal de 7h00 à 10h30, à 1 200 EGP par adulte.", "J'aurai besoin d'une option végétarienne — réservation {BID}.",
 "C'est noté — une demande de petit-déjeuner végétarien figure sur la réservation {BID} pour votre séjour à partir du {CI}. L'hôtel confirmera.", "Merci.", "Je vous en prie."],
'Russian': ["Во сколько подают завтрак?", "Завтрак подают в основном ресторане с 7:00 до 10:30, стоимость 1 200 EGP со взрослого.", "Мне нужен вегетарианский вариант — бронь {BID}.",
 "Отмечено — запрос на вегетарианский завтрак добавлен в бронь {BID} с датой заезда {CI}. Отель подтвердит.", "Спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["الفطار الساعة كام؟", "الفطار في المطعم الرئيسي من 7 لـ 10 ونص الصبح، بـ 1,200 جنيه للفرد.", "هحتاج فطار نباتي، والحجز رقم {BID}.",
 "اتسجل — طلب فطار نباتي على الحجز {BID} لإقامتك اللي بتبدأ يوم {CI}، والفندق هيأكد.", "شكراً.", "العفو."],
}
T['INT013_F4'] = {
'English': ["Does the hotel have a spa?", "Yes — the spa is open from 9:00 AM to 10:00 PM, and a 60-minute massage is 3,500 EGP.", "Please book me a session. My booking is {BID}.",
 "I've requested a spa session on booking {BID} for your stay from {CI} to {CO}. The spa team will confirm the day and time with you.", "Thanks.", "You're welcome."],
'Arabic': ["هل يوجد سبا في الفندق؟", "نعم، السبا مفتوح من 9:00 صباحاً حتى 10:00 مساءً، ومساج 60 دقيقة بسعر 3,500 جنيه مصري.", "احجز لي جلسة من فضلك. رقم حجزي {BID}.",
 "طلبت جلسة سبا على الحجز {BID} لإقامتك من {CI} إلى {CO}، وسيؤكد فريق السبا معك اليوم والموعد.", "شكراً.", "على الرحب والسعة."],
'French': ["L'hôtel a-t-il un spa ?", "Oui — le spa est ouvert de 9h00 à 22h00, et un massage de 60 minutes coûte 3 500 EGP.", "Réservez-moi une séance, s'il vous plaît. Ma réservation est {BID}.",
 "J'ai demandé une séance de spa sur la réservation {BID} pour votre séjour du {CI} au {CO}. L'équipe du spa vous confirmera le jour et l'heure.", "Merci.", "Je vous en prie."],
'Russian': ["В отеле есть спа?", "Да, спа работает с 9:00 до 22:00, массаж 60 минут стоит 3 500 EGP.", "Запишите меня на сеанс, пожалуйста. Моя бронь — {BID}.",
 "Я запросил сеанс спа по брони {BID} на период с {CI} по {CO}. Команда спа подтвердит с вами день и время.", "Спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["في سبا في الفندق؟", "أيوة، السبا مفتوح من 9 الصبح لـ 10 بالليل، ومساج الساعة بـ 3,500 جنيه.", "احجزلي جلسة لو سمحت. رقم الحجز {BID}.",
 "طلبت جلسة سبا على الحجز {BID} لإقامتك من {CI} لـ {CO}، وفريق السبا هيأكد معاك اليوم والميعاد.", "شكراً.", "العفو."],
}
OPENERS['INT013_F5'] = {
 'English': ["I am arriving by car. What facilities do you have?", "What amenities are there at the hotel?", "Tell me about the hotel facilities."],
 'Arabic': ["سأصل بالسيارة. ما المرافق المتوفرة لديكم؟", "ما وسائل الراحة الموجودة في الفندق؟", "حدثني عن مرافق الفندق."],
 'French': ["J'arrive en voiture. Quels équipements proposez-vous ?", "Quelles sont les commodités de l'hôtel ?", "Parlez-moi des équipements de l'hôtel."],
 'Russian': ["Я приеду на машине. Какие у вас есть удобства?", "Какие удобства есть в отеле?", "Расскажите об удобствах отеля."],
 'Arabic-Egyptian': ["أنا جاي بالعربية. عندكم إيه من المرافق؟", "الفندق فيه إيه من الخدمات؟", "احكيلي عن مرافق الفندق."]}
PARK_Q = {'English': "Is there parking for guests?", 'Arabic': "هل تتوفر مواقف للنزلاء؟", 'French': "Y a-t-il un parking pour les clients ?", 'Russian': "Есть ли парковка для гостей?", 'Arabic-Egyptian': "في ركنة للنزلاء؟"}
PARK_A = {'English': "Yes, parking is available for hotel guests.", 'Arabic': "نعم، مواقف السيارات متاحة لنزلاء الفندق.", 'French': "Oui, un parking est disponible pour les clients de l'hôtel.",
          'Russian': "Да, для гостей отеля есть парковка.", 'Arabic-Egyptian': "أيوة، في جراج متاح لنزلاء الفندق."}
T['INT013_F5'] = {l: [None, FAC[l], PARK_Q[l], PARK_A[l], CLOSE[l][0], CLOSE[l][1]] for l in L}

# ───────────────────────── INT014 emergencies ─────────────────────────
T['INT014_F1'] = {
'English': ["Someone in my room is unwell and needs a doctor.", "Please call reception from the room phone right away — the hotel can arrange a doctor or emergency medical services. If it is life-threatening, contact the emergency services directly. Which room are you in?",
 "Room {ROOM}.", "Reception has been alerted for room {ROOM} and help is on its way. First aid is available at reception.", "Thank you."],
'Arabic': ["شخص معي في الغرفة متعب ويحتاج إلى طبيب.", "اتصل بمكتب الاستقبال من هاتف الغرفة فوراً، فالفندق يمكنه ترتيب طبيب أو خدمات طبية طارئة. وإذا كانت الحالة تهدد الحياة فاتصل بخدمات الطوارئ مباشرة. في أي غرفة أنت؟",
 "الغرفة {ROOM}.", "أُبلغ مكتب الاستقبال بالغرفة {ROOM} والمساعدة في الطريق إليك. الإسعافات الأولية متوفرة في الاستقبال.", "شكراً لك."],
'French': ["Une personne dans ma chambre ne se sent pas bien et a besoin d'un médecin.", "Appelez tout de suite la réception depuis le téléphone de la chambre — l'hôtel peut faire venir un médecin ou des secours médicaux. Si la vie est en danger, contactez directement les services d'urgence. Dans quelle chambre êtes-vous ?",
 "Chambre {ROOM}.", "La réception a été alertée pour la chambre {ROOM} et l'aide arrive. Les premiers secours sont disponibles à la réception.", "Merci."],
'Russian': ["Человеку в моём номере плохо, нужен врач.", "Сразу позвоните на стойку регистрации с телефона в номере — отель может вызвать врача или экстренную медицинскую помощь. Если есть угроза жизни, звоните в экстренные службы напрямую. В каком вы номере?",
 "Номер {ROOM}.", "Стойку регистрации оповестили о номере {ROOM}, помощь уже идёт. Первая помощь есть на стойке регистрации.", "Спасибо."],
'Arabic-Egyptian': ["في حد معايا في الأوضة تعبان ومحتاج دكتور.", "كلّم الاستقبال من تليفون الأوضة حالاً، الفندق يقدر يجيب دكتور أو إسعاف. ولو الحالة خطر على الحياة كلّم الطوارئ على طول. انت في أوضة كام؟",
 "أوضة {ROOM}.", "الاستقبال اتبلغ بأوضة {ROOM} والمساعدة جاية في الطريق. وفي إسعافات أولية في الاستقبال.", "شكراً."],
}
T['INT014_F2'] = {
'English': ["Water is leaking in my bathroom and I can't stop it.", "I'll get maintenance to you urgently. What is your room number?", "Room {ROOM}.",
 "I've reported an urgent water leak in room {ROOM} to maintenance. If the room can't be used, reception can arrange another one, subject to availability.", "Thanks."],
'Arabic': ["هناك تسرب مياه في حمامي ولا أستطيع إيقافه.", "سأرسل إليك الصيانة بشكل عاجل. ما رقم غرفتك؟", "الغرفة {ROOM}.",
 "أبلغت الصيانة بتسرب مياه عاجل في الغرفة {ROOM}. وإذا تعذر استخدام الغرفة يمكن للاستقبال ترتيب غرفة أخرى حسب التوافر.", "شكراً."],
'French': ["De l'eau fuit dans ma salle de bain et je n'arrive pas à l'arrêter.", "Je vous envoie la maintenance en urgence. Quel est votre numéro de chambre ?", "Chambre {ROOM}.",
 "J'ai signalé une fuite d'eau urgente dans la chambre {ROOM} à la maintenance. Si la chambre est inutilisable, la réception peut vous en attribuer une autre, selon disponibilité.", "Merci."],
'Russian': ["В ванной течёт вода, и я не могу её остановить.", "Срочно направлю к вам техническую службу. Какой у вас номер?", "Номер {ROOM}.",
 "Я сообщил в техническую службу о срочной протечке в номере {ROOM}. Если номером нельзя пользоваться, стойка регистрации может предоставить другой при наличии.", "Спасибо."],
'Arabic-Egyptian': ["في مية بتخر في الحمام ومش عارف أوقفها.", "هبعتلك الصيانة حالاً. رقم أوضتك كام؟", "أوضة {ROOM}.",
 "بلّغت الصيانة بتسريب مية مستعجل في أوضة {ROOM}. ولو الأوضة مابقتش تنفع، الاستقبال يقدر يديك أوضة تانية على حسب المتاح.", "شكراً."],
}
T['INT014_F3'] = {
'English': ["I think something has been stolen from my room.", "I'm sorry. This needs to go to reception straight away — what is your room number?", "Room {ROOM}.",
 "Reception and security have been notified for room {ROOM} and will come to you. In the meantime, please keep the door locked and use the room safe for valuables.", "Okay."],
'Arabic': ["أظن أن شيئاً سُرق من غرفتي.", "نأسف لذلك. يجب إبلاغ الاستقبال فوراً، ما رقم غرفتك؟", "الغرفة {ROOM}.",
 "أُبلغ الاستقبال والأمن بشأن الغرفة {ROOM} وسيحضرون إليك. وفي الأثناء، أبقِ الباب مغلقاً واستخدم خزنة الغرفة للأشياء الثمينة.", "حسناً."],
'French': ["Je pense qu'on m'a volé quelque chose dans ma chambre.", "Je suis désolé. Il faut prévenir la réception immédiatement — quel est votre numéro de chambre ?", "Chambre {ROOM}.",
 "La réception et la sécurité ont été prévenues pour la chambre {ROOM} et vont venir vous voir. En attendant, gardez la porte fermée à clé et utilisez le coffre-fort pour vos objets de valeur.", "D'accord."],
'Russian': ["Кажется, из моего номера что-то украли.", "Сожалеем. Об этом нужно сразу сообщить на стойку регистрации — какой у вас номер?", "Номер {ROOM}.",
 "Стойка регистрации и служба безопасности оповещены о номере {ROOM} и подойдут к вам. Пока держите дверь запертой и храните ценности в сейфе.", "Хорошо."],
'Arabic-Egyptian': ["أظن في حاجة اتسرقت من أوضتي.", "آسفين. لازم الاستقبال يتبلغ حالاً، رقم أوضتك كام؟", "أوضة {ROOM}.",
 "الاستقبال والأمن اتبلغوا بأوضة {ROOM} وجايين لك. لحد ما ييجوا اقفل الباب واستخدم الخزنة للحاجات الغالية.", "ماشي."],
}
T['INT014_F4'] = {
'English': ["It's the middle of the night and the power in my room has gone off.", "Reception is staffed 24/7 and can help right now. What is your room number?", "Room {ROOM}.",
 "Reception has been informed about the power outage in room {ROOM} and will assist you now.", "Thank you."],
'Arabic': ["نحن في منتصف الليل وانقطعت الكهرباء في غرفتي.", "مكتب الاستقبال يعمل على مدار الساعة ويمكنه المساعدة الآن. ما رقم غرفتك؟", "الغرفة {ROOM}.",
 "أُبلغ مكتب الاستقبال بانقطاع الكهرباء في الغرفة {ROOM} وسيساعدك الآن.", "شكراً لك."],
'French': ["C'est le milieu de la nuit et il n'y a plus d'électricité dans ma chambre.", "La réception est ouverte 24h/24 et peut vous aider tout de suite. Quel est votre numéro de chambre ?", "Chambre {ROOM}.",
 "La réception a été informée de la coupure de courant dans la chambre {ROOM} et vous vient en aide maintenant.", "Merci."],
'Russian': ["Сейчас глубокая ночь, и в моём номере пропало электричество.", "Стойка регистрации работает круглосуточно и поможет прямо сейчас. Какой у вас номер?", "Номер {ROOM}.",
 "Стойке регистрации сообщили об отключении электричества в номере {ROOM}, вам сейчас помогут.", "Спасибо."],
'Arabic-Egyptian': ["إحنا في نص الليل والنور قطع في الأوضة.", "الاستقبال شغال 24 ساعة ويقدر يساعدك دلوقتي. رقم أوضتك كام؟", "أوضة {ROOM}.",
 "الاستقبال اتبلغ إن النور قاطع في أوضة {ROOM} وهيساعدك دلوقتي.", "شكراً."],
}
OPENERS['INT014_F5'] = {
 'English': ["The fire alarm is going off on my floor!", "There is an alarm sounding — what do I do?", "I can smell smoke in the corridor."],
 'Arabic': ["جرس إنذار الحريق يرن في طابقي!", "هناك إنذار يرن، ماذا أفعل؟", "أشم رائحة دخان في الممر."],
 'French': ["L'alarme incendie sonne à mon étage !", "Une alarme sonne — que dois-je faire ?", "Je sens une odeur de fumée dans le couloir."],
 'Russian': ["На моём этаже сработала пожарная сигнализация!", "Звучит сигнал тревоги — что мне делать?", "В коридоре пахнет дымом."],
 'Arabic-Egyptian': ["جرس الحريق بيضرب في الدور بتاعي!", "في إنذار بيرن، أعمل إيه؟", "شامم ريحة دخان في الطرقة."]}
T['INT014_F5'] = {
'English': [None, "Please leave now using the marked emergency exits and follow staff instructions. Use the stairs, not the elevators, and go to the assembly point.", "Okay, we're going.",
 "Wait at the assembly point and don't return to your room until staff say it is safe."],
'Arabic': [None, "غادر الآن عبر مخارج الطوارئ المحددة واتبع تعليمات الموظفين. استخدم السلالم لا المصاعد، وتوجه إلى نقطة التجمع.", "حسناً، نحن في الطريق.",
 "انتظر في نقطة التجمع ولا تعد إلى غرفتك حتى يؤكد الموظفون أن ذلك آمن."],
'French': [None, "Quittez les lieux maintenant par les sorties de secours balisées et suivez les instructions du personnel. Prenez les escaliers, pas les ascenseurs, et rejoignez le point de rassemblement.", "D'accord, nous y allons.",
 "Attendez au point de rassemblement et ne retournez pas dans votre chambre avant que le personnel ne l'autorise."],
'Russian': [None, "Покиньте помещение сейчас через обозначенные эвакуационные выходы и следуйте указаниям персонала. Используйте лестницу, а не лифт, и идите к месту сбора.", "Хорошо, выходим.",
 "Ждите на месте сбора и не возвращайтесь в номер, пока персонал не скажет, что это безопасно."],
'Arabic-Egyptian': [None, "اخرج دلوقتي من مخارج الطوارئ اللي عليها علامات واتبع تعليمات الموظفين. انزل على السلم مش الأسانسير، وروح نقطة التجمع.", "حاضر، إحنا نازلين.",
 "استنى في نقطة التجمع وماترجعش أوضتك غير لما الموظفين يقولولك إن الوضع أمان."],
}


# ───────────────────────── v5: identity check, rate plans, spoken dates ─────────────────────────
# RULE (reservation_security.txt): before discussing, changing or cancelling a booking the agent
# asks for the booking reference AND the last name on it. Applied to every flow that changes a
# booking or reads its money back.
_ID_ASK = {
 'English': [("What is your booking reference?", "What is your booking reference and the last name on the booking?"),
             ("And what is your booking reference?", "And what is your booking reference and the last name on the booking?")],
 'Arabic': [("وما رقم الحجز؟", "وما رقم الحجز واسم العائلة المسجل فيه؟"), ("ما رقم الحجز؟", "ما رقم الحجز واسم العائلة المسجل فيه؟")],
 'French': [("Quel est votre numéro de réservation ?", "Quel est votre numéro de réservation et le nom de famille de la réservation ?")],
 'Russian': [("И какой у вас номер брони?", "И какой у вас номер брони и фамилия в ней?"), ("Какой номер брони?", "Какой номер брони и фамилия в ней?")],
 'Arabic-Egyptian': [("وقوللي رقم الحجز.", "وقوللي رقم الحجز واسم العيلة اللي عليه."), ("رقم الحجز كام؟", "رقم الحجز كام واسم العيلة اللي عليه؟")],
}
_ID_USER = {
 'English': [("It's {BID}. ", "It's {BID}, last name {LAST}. "), ("{BID}. ", "{BID}, {LAST}. ")],
 'Arabic': [("رقم الحجز {BID}، ", "رقم الحجز {BID} باسم {LAST}، "), ("{BID}. ", "{BID}، {LAST}. ")],
 'French': [("C'est {BID}. ", "C'est {BID}, au nom de {LAST}. "), ("{BID}. ", "{BID}, {LAST}. ")],
 'Russian': [("Бронь {BID}. ", "Бронь {BID}, фамилия {LAST}. "), ("{BID}. ", "{BID}, {LAST}. ")],
 'Arabic-Egyptian': [("رقм الحجز {BID}، ".replace('м', 'م'), "رقم الحجز {BID} باسم {LAST}، "), ("{BID}. ", "{BID}، {LAST}. ")],
}
for _flow in ('INT009_F1', 'INT009_F2', 'INT009_F3', 'INT009_F4', 'INT009_F5', 'INT010_F3'):
    for _L in L:
        turns = T[_flow][_L]
        for i, t in enumerate(turns):
            if isinstance(t, str):
                for a, b in (_ID_ASK[_L] if i % 2 else []):
                    if a in t: t = t.replace(a, b); break
                if i % 2 == 0:
                    if t == '{BID}.': t = {'English': '{BID}, {LAST}.', 'French': '{BID}, {LAST}.', 'Russian': '{BID}, фамилия {LAST}.'}.get(_L, '{BID}، {LAST}.')
                    else:
                        for a, b in _ID_USER[_L]:
                            if t.startswith(a): t = b + t[len(a):]; break
                turns[i] = t

RATE = {'English': {'Flexible': 'Flexible', 'Non-refundable': 'Non-refundable'},
        'Arabic': {'Flexible': 'المرن', 'Non-refundable': 'غير القابل للاسترداد'},
        'French': {'Flexible': 'flexible', 'Non-refundable': 'non remboursable'},
        'Russian': {'Flexible': 'гибкий', 'Non-refundable': 'невозвратный'},
        'Arabic-Egyptian': {'Flexible': 'المرن', 'Non-refundable': 'اللي مش بيترد'}}
MONTHS = {
 'English': 'January February March April May June July August September October November December'.split(),
 'French': 'janvier février mars avril mai juin juillet août septembre octobre novembre décembre'.split(),
 'Russian': 'января февраля марта апреля мая июня июля августа сентября октября ноября декабря'.split(),
 'Arabic': 'يناير فبراير مارس أبريل مايو يونيو يوليو أغسطس سبتمبر أكتوبر نوفمبر ديسمبر'.split(),
}
MONTHS['Arabic-Egyptian'] = MONTHS['Arabic']
def spoken_date(iso, lang, this_year=2026):
    """2026-10-14 → '14 October' / '14 octobre' / '14 октября' / '14 أكتوبر' (year added only if not this_year)."""
    y, m, d = (int(x) for x in iso[:10].split('-'))
    day = '1er' if lang == 'French' and d == 1 else str(d)
    out = f'{day} {MONTHS[lang][m - 1]}'
    return out + (f' {y}' if y != this_year else '')

ITEM = {  # menu item names used in the room-service flow
 'M07': {'English': 'the beef burger', 'Arabic': 'برجر اللحم', 'French': 'le burger de bœuf', 'Russian': 'бургер с говядиной', 'Arabic-Egyptian': 'برجر لحمة'},
 'M23': {'English': 'a fresh orange juice', 'Arabic': 'عصير برتقال طازج', 'French': 'un jus d\'orange frais', 'Russian': 'свежевыжатый апельсиновый сок', 'Arabic-Egyptian': 'عصير برتقال فريش'},
 'M15': {'English': 'the koshary', 'Arabic': 'كشري', 'French': 'le koshary', 'Russian': 'кошари', 'Arabic-Egyptian': 'كشري'},
 'M20': {'English': 'a tea', 'Arabic': 'شاي', 'French': 'un thé', 'Russian': 'чай', 'Arabic-Egyptian': 'شاي'},
 'M04': {'English': 'the lentil soup', 'Arabic': 'شوربة عدس', 'French': 'la soupe de lentilles', 'Russian': 'чечевичный суп', 'Arabic-Egyptian': 'شوربة عدس'},
 'M17': {'English': 'the Om Ali', 'Arabic': 'أم علي', 'French': 'l\'Om Ali', 'Russian': 'Ом Али', 'Arabic-Egyptian': 'أم علي'},
}

# ── new flows ──
T['INT031_F1'] = {
'English': ["Can I order some food to my room?", "Of course — room service runs 24 hours. What would you like, and what is your room number?",
 "Room {ROOM}. I'd like {I1} and {I2}, please.",
 "That's {I1} at {P1} EGP and {I2} at {P2} EGP, plus the 300 EGP delivery charge: {SUM} EGP in total, charged to room {ROOM}. It will arrive in 30 to 45 minutes. Anything else?",
 "No, that's all.", "Enjoy your meal."],
'Arabic': ["هل يمكنني طلب طعام إلى غرفتي؟", "بالتأكيد، خدمة الغرف متاحة على مدار الساعة. ماذا تود أن تطلب، وما رقم غرفتك؟",
 "الغرفة {ROOM}. أريد {I1} و{I2} من فضلك.",
 "{I1} بسعر {P1} جنيه مصري و{I2} بسعر {P2} جنيه مصري، مع رسم التوصيل 300 جنيه مصري، فيكون الإجمالي {SUM} جنيه مصري على حساب الغرفة {ROOM}. سيصل الطلب خلال 30 إلى 45 دقيقة. هل تحتاج شيئاً آخر؟",
 "لا، هذا كل شيء.", "بالهناء والشفاء."],
'French': ["Puis-je commander à manger dans ma chambre ?", "Bien sûr, le room service fonctionne 24h/24. Que souhaitez-vous, et quel est votre numéro de chambre ?",
 "Chambre {ROOM}. Je voudrais {I1} et {I2}, s'il vous plaît.",
 "Donc {I1} à {P1} EGP et {I2} à {P2} EGP, plus 300 EGP de frais de livraison : {SUM} EGP au total, portés sur la chambre {ROOM}. Livraison dans 30 à 45 minutes. Autre chose ?",
 "Non, ce sera tout.", "Bon appétit."],
'Russian': ["Можно заказать еду в номер?", "Конечно, обслуживание номеров работает круглосуточно. Что вы хотели бы заказать и какой у вас номер?",
 "Номер {ROOM}. Мне {I1} и {I2}, пожалуйста.",
 "Итак, {I1} за {P1} EGP и {I2} за {P2} EGP, плюс доставка 300 EGP: всего {SUM} EGP на счёт номера {ROOM}. Заказ прибудет через 30–45 минут. Что-нибудь ещё?",
 "Нет, это всё.", "Приятного аппетита."],
'Arabic-Egyptian': ["ينفع أطلب أكل للأوضة؟", "أكيد، الروم سيرفس شغال 24 ساعة. تحب تطلب إيه، وأوضتك رقم كام؟",
 "أوضة {ROOM}. عايز {I1} و{I2} لو سمحت.",
 "{I1} بـ {P1} جنيه و{I2} بـ {P2} جنيه، وفوقهم 300 جنيه توصيل، يبقى الإجمالي {SUM} جنيه على حساب أوضة {ROOM}. الطلب هيوصل خلال 30 لـ 45 دقيقة. محتاج حاجة تانية؟",
 "لأ، كده تمام.", "بالهنا والشفا."],
}
T['INT027_F1'] = {
'English': ["I have a discount code, {CODE}. Can I use it?",
 {'active': "Yes — {CODE} is valid until {END}: {DISC}. Only one discount applies per booking, so it replaces any other offer. Shall I apply it to a new booking?",
  'exhausted': "I'm sorry — {CODE} has reached its usage limit, so it can no longer be applied. The Non-refundable rate, 15% below the Flexible rate, is an alternative.",
  'scheduled': "{CODE} is not valid yet: it runs from {START} to {END}. It can be used for bookings made from {START}."},
 "Okay, thanks.", "You're welcome."],
'Arabic': ["لديّ كود خصم {CODE}. هل يمكنني استخدامه؟",
 {'active': "نعم، الكود {CODE} ساري حتى {END}: {DISC}. يُطبَّق خصم واحد فقط على الحجز، لذا يحل محل أي عرض آخر. هل أطبقه على حجز جديد؟",
  'exhausted': "نأسف، الكود {CODE} بلغ الحد الأقصى للاستخدام ولم يعد ممكناً تطبيقه. يمكنك بدلاً منه اختيار السعر غير القابل للاسترداد بخصم 15% عن السعر المرن.",
  'scheduled': "الكود {CODE} لم يبدأ سريانه بعد: يسري من {START} حتى {END}، ويمكن استخدامه للحجوزات التي تتم بدءاً من {START}."},
 "حسناً، شكراً.", "على الرحب والسعة."],
'French': ["J'ai un code de réduction, {CODE}. Puis-je l'utiliser ?",
 {'active': "Oui — {CODE} est valable jusqu'au {END} : {DISC}. Une seule remise s'applique par réservation, il remplace donc toute autre offre. Dois-je l'appliquer à une nouvelle réservation ?",
  'exhausted': "Désolé — {CODE} a atteint sa limite d'utilisation et ne peut plus être appliqué. Le tarif non remboursable, 15 % sous le tarif flexible, est une alternative.",
  'scheduled': "{CODE} n'est pas encore valable : il court du {START} au {END}. Il pourra servir pour les réservations faites à partir du {START}."},
 "D'accord, merci.", "Je vous en prie."],
'Russian': ["У меня есть промокод {CODE}. Можно им воспользоваться?",
 {'active': "Да — {CODE} действует до {END}: {DISC}. К бронированию применяется только одна скидка, поэтому код заменяет другие предложения. Применить его к новому бронированию?",
  'exhausted': "К сожалению, {CODE} исчерпал лимит использований и больше не применяется. Альтернатива — невозвратный тариф, на 15 % ниже гибкого.",
  'scheduled': "{CODE} ещё не действует: срок действия с {START} по {END}. Его можно использовать для бронирований, сделанных начиная с {START}."},
 "Хорошо, спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["معايا كود خصم {CODE}، ينفع أستخدمه؟",
 {'active': "أيوة، الكود {CODE} شغال لحد {END}: {DISC}. وخصم واحد بس على الحجز، فهيبقى بدل أي عرض تاني. أطبقهولك على حجز جديد؟",
  'exhausted': "للأسف الكود {CODE} خلص عدد استخداماته ومبقاش ينفع. ممكن بداله تحجز بالسعر اللي مش بيترد، أرخص 15% من المرن.",
  'scheduled': "الكود {CODE} لسه مابداش: شغال من {START} لحد {END}، وينفع في الحجوزات اللي تتعمل من {START}."},
 "ماشي، شكراً.", "العفو."],
}
DISC = {'English': {'PERCENTAGE': '{V}% off the room rate', 'FIXED_AMOUNT': '{V} EGP off the stay'},
        'Arabic': {'PERCENTAGE': 'خصم {V}% على سعر الغرفة', 'FIXED_AMOUNT': 'خصم {V} جنيه مصري على الإقامة'},
        'French': {'PERCENTAGE': '{V} % de remise sur le tarif', 'FIXED_AMOUNT': '{V} EGP de remise sur le séjour'},
        'Russian': {'PERCENTAGE': 'скидка {V} % на номер', 'FIXED_AMOUNT': 'скидка {V} EGP на проживание'},
        'Arabic-Egyptian': {'PERCENTAGE': 'خصم {V}% على سعر الأوضة', 'FIXED_AMOUNT': 'خصم {V} جنيه على الإقامة'}}
T['INT007_F1'] = {
'English': ["Can I check out late, around 4 PM?", "Let me check. What is your room number?", "Room {ROOM}.",
 {'pay': "You check out on {CO}. Late check-out until 4:00 PM costs 1,500 EGP, subject to availability; until 6:00 PM it would be 50% of the nightly rate. Shall I request 4:00 PM?",
  'plat': "You check out on {CO}, and as a Platinum member late check-out until 4:00 PM is free of charge, subject to availability. Shall I request it?"},
 "Yes, please.", "Done — late check-out until 4:00 PM is requested for room {ROOM}. Reception will confirm on the morning of departure."],
'Arabic': ["هل يمكنني المغادرة متأخراً، حوالي الرابعة عصراً؟", "دعني أتحقق. ما رقم غرفتك؟", "الغرفة {ROOM}.",
 {'pay': "موعد مغادرتك يوم {CO}. المغادرة المتأخرة حتى 4:00 عصراً بسعر 1,500 جنيه مصري حسب التوافر، وحتى 6:00 مساءً بنسبة 50% من سعر الليلة. هل أطلبها حتى 4:00 عصراً؟",
  'plat': "موعد مغادرتك يوم {CO}، وبصفتك عضواً بلاتينياً فالمغادرة المتأخرة حتى 4:00 عصراً مجانية حسب التوافر. هل أطلبها؟"},
 "نعم، من فضلك.", "تم طلب المغادرة المتأخرة حتى 4:00 عصراً للغرفة {ROOM}، وسيؤكدها الاستقبال صباح يوم المغادرة."],
'French': ["Puis-je partir tard, vers 16h00 ?", "Je vérifie. Quel est votre numéro de chambre ?", "Chambre {ROOM}.",
 {'pay': "Votre départ est le {CO}. Le départ tardif jusqu'à 16h00 coûte 1 500 EGP, selon disponibilité ; jusqu'à 18h00, ce serait 50 % du tarif de la nuit. Dois-je demander 16h00 ?",
  'plat': "Votre départ est le {CO} et, en tant que membre Platinum, le départ tardif jusqu'à 16h00 est gratuit, selon disponibilité. Dois-je le demander ?"},
 "Oui, s'il vous plaît.", "C'est fait — le départ tardif jusqu'à 16h00 est demandé pour la chambre {ROOM}. La réception le confirmera le matin du départ."],
'Russian': ["Можно выехать попозже, около 16:00?", "Сейчас проверю. Какой у вас номер?", "Номер {ROOM}.",
 {'pay': "Ваш выезд {CO}. Поздний выезд до 16:00 стоит 1 500 EGP при наличии; до 18:00 — 50 % стоимости ночи. Запросить выезд в 16:00?",
  'plat': "Ваш выезд {CO}, и как участник уровня Platinum вы можете бесплатно выехать до 16:00 при наличии. Запросить?"},
 "Да, пожалуйста.", "Готово — поздний выезд до 16:00 для номера {ROOM} запрошен. Стойка регистрации подтвердит утром в день выезда."],
'Arabic-Egyptian': ["ينفع أخرج متأخر، حوالي 4 العصر؟", "ثانية أشوف. أوضتك رقم كام؟", "أوضة {ROOM}.",
 {'pay': "خروجك يوم {CO}. الخروج المتأخر لحد 4 العصر بـ 1,500 جنيه على حسب المتاح، ولحد 6 بنص سعر الليلة. أطلبهولك لحد 4؟",
  'plat': "خروجك يوم {CO}، وعشان انت عضو بلاتيني الخروج لحد 4 العصر ببلاش على حسب المتاح. أطلبهولك؟"},
 "أيوة لو سمحت.", "تمام، اتطلب خروج متأخر لحد 4 العصر لأوضة {ROOM}، والاستقبال هيأكده صباح يوم الخروج."],
}
T['INT021_F1'] = {
'English': ["Will I have to pay anything when I check in?", "I can check. What is your booking reference and the last name on the booking?", "{BID}, {LAST}.",
 {'flex': "Booking {BID} is a {TYPE} from {CI} to {CO} on the Flexible rate, so the stay of {TOTAL} EGP is paid at the hotel, at check-in or check-out. At check-in we also take a refundable deposit of 3,000 EGP per night — {DEP} EGP for your stay — by card hold or cash, released at check-out.",
  'nr': "Booking {BID} is a {TYPE} from {CI} to {CO} on the Non-refundable rate and is already paid in full, so the only thing at check-in is the refundable deposit of 3,000 EGP per night — {DEP} EGP for your stay — released at check-out."},
 "Understood, thanks.", "You're welcome."],
'Arabic': ["هل سأدفع أي شيء عند تسجيل الوصول؟", "يمكنني التحقق. ما رقم الحجز واسم العائلة المسجل فيه؟", "{BID}، {LAST}.",
 {'flex': "الحجز {BID} هو {TYPE} من {CI} إلى {CO} بالسعر المرن، لذا تُدفع قيمة الإقامة البالغة {TOTAL} جنيه مصري في الفندق عند الوصول أو المغادرة. وعند تسجيل الوصول نأخذ أيضاً تأميناً مسترداً قدره 3,000 جنيه مصري لكل ليلة، أي {DEP} جنيه مصري لإقامتك، بحجز على البطاقة أو نقداً، ويُفرج عنه عند المغادرة.",
  'nr': "الحجز {BID} هو {TYPE} من {CI} إلى {CO} بالسعر غير القابل للاسترداد ومدفوع بالكامل، لذا لا يبقى عند الوصول سوى التأمين المسترد بقيمة 3,000 جنيه مصري لكل ليلة، أي {DEP} جنيه مصري لإقامتك، ويُفرج عنه عند المغادرة."},
 "مفهوم، شكراً.", "على الرحب والسعة."],
'French': ["Devrai-je payer quelque chose à l'arrivée ?", "Je vérifie. Quel est votre numéro de réservation et le nom de famille de la réservation ?", "{BID}, {LAST}.",
 {'flex': "La réservation {BID} est une {TYPE} du {CI} au {CO} au tarif flexible : le séjour de {TOTAL} EGP se paie à l'hôtel, à l'arrivée ou au départ. À l'arrivée, nous prenons aussi une caution remboursable de 3 000 EGP par nuit, soit {DEP} EGP pour votre séjour, par blocage sur carte ou en espèces, libérée au départ.",
  'nr': "La réservation {BID} est une {TYPE} du {CI} au {CO} au tarif non remboursable, déjà payée intégralement : à l'arrivée, il n'y a que la caution remboursable de 3 000 EGP par nuit, soit {DEP} EGP pour votre séjour, libérée au départ."},
 "Compris, merci.", "Je vous en prie."],
'Russian': ["Нужно ли будет что-то платить при заселении?", "Могу проверить. Какой номер брони и фамилия в ней?", "{BID}, фамилия {LAST}.",
 {'flex': "Бронь {BID}: {TYPE}, с {CI} по {CO}, гибкий тариф, поэтому проживание стоимостью {TOTAL} EGP оплачивается в отеле при заезде или выезде. При заселении мы также берём возвратный депозит 3 000 EGP за ночь — {DEP} EGP за ваше проживание — блокировкой на карте или наличными; он снимается при выезде.",
  'nr': "Бронь {BID}: {TYPE}, с {CI} по {CO}, невозвратный тариф, уже оплачена полностью, поэтому при заселении берётся только возвратный депозит 3 000 EGP за ночь — {DEP} EGP за ваше проживание, — он снимается при выезде."},
 "Понятно, спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["هدفع أي حاجة وأنا بعمل check-in؟", "أقدر أشوفلك. رقم الحجز كام واسم العيلة اللي عليه؟", "{BID}، {LAST}.",
 {'flex': "الحجز {BID} {TYPE} من {CI} لـ {CO} بالسعر المرن، يعني الإقامة وقيمتها {TOTAL} جنيه بتتدفع في الفندق وقت الدخول أو الخروج. ووقت الدخول بناخد كمان تأمين بيرجع 3,000 جنيه عن كل ليلة، يعني {DEP} جنيه لإقامتك، على الكارت أو كاش، وبيرجع وقت الخروج.",
  'nr': "الحجز {BID} {TYPE} من {CI} لـ {CO} بالسعر اللي مش بيترد ومدفوع كله، فوقت الدخول مفيش غير التأمين اللي بيرجع 3,000 جنيه عن كل ليلة، يعني {DEP} جنيه لإقامتك، وبيرجع وقت الخروج."},
 "تمام، شكراً.", "العفو."],
}
# ── rewritten money flows (replace the hand-written CANCEL_F1/F2, PAY_F1/F2) ──
T['CANCEL_F1_standard'] = {
'English': ["I need to cancel my booking.", "I can help. What is the booking reference, and the last name on the booking?", "{BID}, {LAST}.",
 "Thank you. Booking {BID} is a {TYPE} from {CI} to {CO} on the Flexible rate. You are cancelling more than 48 hours before arrival, so it is free of charge. Shall I go ahead?",
 "Yes, cancel it. Will I get my money back?",
 {'paid': "Done — {BID} is cancelled and the confirmation is on its way by email. The {PAID} EGP you paid goes back to your original payment method: we process it within 3 business days, and cards usually show it 7 to 14 business days later.",
  'unpaid': "Done — {BID} is cancelled and the confirmation is on its way by email. Nothing was charged on the Flexible rate, so there is nothing to refund."}],
'Arabic': ["أحتاج إلى إلغاء حجزي.", "يمكنني المساعدة. ما رقم الحجز واسم العائلة المسجل فيه؟", "{BID}، {LAST}.",
 "شكراً لك. الحجز {BID} هو {TYPE} من {CI} إلى {CO} بالسعر المرن، وأنت تلغي قبل الوصول بأكثر من 48 ساعة، لذا فالإلغاء مجاني. هل أتابع؟",
 "نعم، ألغِه. هل سأسترد أموالي؟",
 {'paid': "تم، أُلغي الحجز {BID} والتأكيد في طريقه إلى بريدك الإلكتروني. سيُرد مبلغ {PAID} جنيه مصري إلى وسيلة الدفع الأصلية: نعالجه خلال 3 أيام عمل، ويظهر عادةً على البطاقة بعد 7 إلى 14 يوم عمل.",
  'unpaid': "تم، أُلغي الحجز {BID} والتأكيد في طريقه إلى بريدك الإلكتروني. لم يُخصم أي مبلغ في السعر المرن، لذا لا يوجد ما يُسترد."}],
'French': ["Je dois annuler ma réservation.", "Je peux vous aider. Quel est le numéro de réservation et le nom de famille de la réservation ?", "{BID}, {LAST}.",
 "Merci. La réservation {BID} est une {TYPE} du {CI} au {CO} au tarif flexible. Vous annulez plus de 48 heures avant l'arrivée, c'est donc gratuit. Je continue ?",
 "Oui, annulez-la. Serai-je remboursé ?",
 {'paid': "C'est fait — {BID} est annulée et la confirmation vous parvient par e-mail. Les {PAID} EGP payés reviennent sur votre moyen de paiement : nous traitons le remboursement sous 3 jours ouvrés, et il apparaît en général sur la carte 7 à 14 jours ouvrés plus tard.",
  'unpaid': "C'est fait — {BID} est annulée et la confirmation vous parvient par e-mail. Rien n'a été débité au tarif flexible, il n'y a donc rien à rembourser."}],
'Russian': ["Мне нужно отменить бронь.", "Помогу. Назовите номер брони и фамилию в ней.", "{BID}, фамилия {LAST}.",
 "Спасибо. Бронь {BID}: {TYPE}, с {CI} по {CO}, гибкий тариф. До заезда больше 48 часов, поэтому отмена бесплатная. Продолжить?",
 "Да, отмените. Деньги вернут?",
 {'paid': "Готово — бронь {BID} отменена, подтверждение придёт на почту. Оплаченные {PAID} EGP вернутся тем же способом оплаты: мы обрабатываем возврат за 3 рабочих дня, на карте он обычно появляется через 7–14 рабочих дней.",
  'unpaid': "Готово — бронь {BID} отменена, подтверждение придёт на почту. По гибкому тарифу ничего не списывалось, поэтому возвращать нечего."}],
'Arabic-Egyptian': ["محتاج ألغي الحجز بتاعي.", "أقدر أساعدك. رقم الحجز كام واسم العيلة اللي عليه؟", "{BID}، {LAST}.",
 "شكراً. الحجز {BID} {TYPE} من {CI} لـ {CO} بالسعر المرن، وانت بتلغي قبل الوصول بأكتر من 48 ساعة، فالإلغاء ببلاش. أكمّل؟",
 "أيوة ألغيه. هتترجعلي فلوسي؟",
 {'paid': "تمام، الحجز {BID} اتلغى والتأكيد جايلك على الإيميل. الـ {PAID} جنيه اللي دفعتهم هيرجعوا على نفس طريقة الدفع: بنعمل الاسترداد خلال 3 أيام عمل، وبيظهر على الكارت عادة بعد 7 لـ 14 يوم عمل.",
  'unpaid': "تمام، الحجز {BID} اتلغى والتأكيد جايلك على الإيميل. في السعر المرن ماكانش اتخصم منك حاجة، فمفيش حاجة ترجع."}],
}
T['CANCEL_F2_nonrefundable'] = {
'English': ["My booking is non-refundable. Can I still cancel it?", "Let me check. What is the booking reference and the last name on the booking?", "{BID}, {LAST}.",
 "Booking {BID} is a {TYPE} from {CI} to {CO} on the Non-refundable rate, paid in full at {TOTAL} EGP. It can be cancelled, but the amount is not refunded, and the dates cannot be changed. Would you still like to cancel?",
 "No, I'll keep it then.", "Understood — booking {BID} stays confirmed. We look forward to welcoming you on {CI}."],
'Arabic': ["حجزي غير قابل للاسترداد. هل ما زال بإمكاني إلغاؤه؟", "دعني أتحقق. ما رقم الحجز واسم العائلة المسجل فيه؟", "{BID}، {LAST}.",
 "الحجز {BID} هو {TYPE} من {CI} إلى {CO} بالسعر غير القابل للاسترداد، ومدفوع بالكامل بقيمة {TOTAL} جنيه مصري. يمكن إلغاؤه لكن المبلغ لا يُسترد، ولا يمكن تغيير تواريخه. هل ما زلت ترغب في الإلغاء؟",
 "لا، سأحتفظ به إذن.", "مفهوم، يبقى الحجز {BID} مؤكداً. نتطلع إلى استقبالك يوم {CI}."],
'French': ["Ma réservation est non remboursable. Puis-je quand même l'annuler ?", "Je vérifie. Quel est le numéro de réservation et le nom de famille de la réservation ?", "{BID}, {LAST}.",
 "La réservation {BID} est une {TYPE} du {CI} au {CO} au tarif non remboursable, payée intégralement ({TOTAL} EGP). Elle peut être annulée, mais le montant n'est pas remboursé, et les dates ne peuvent pas être modifiées. Souhaitez-vous toujours annuler ?",
 "Non, je la garde alors.", "Entendu — la réservation {BID} reste confirmée. Nous vous attendons le {CI}."],
'Russian': ["У меня невозвратная бронь. Можно её всё-таки отменить?", "Сейчас проверю. Какой номер брони и фамилия в ней?", "{BID}, фамилия {LAST}.",
 "Бронь {BID}: {TYPE}, с {CI} по {CO}, невозвратный тариф, оплачена полностью — {TOTAL} EGP. Отменить её можно, но сумма не возвращается, а даты изменить нельзя. Всё равно отменить?",
 "Нет, тогда оставлю.", "Понял — бронь {BID} остаётся подтверждённой. Ждём вас {CI}."],
'Arabic-Egyptian': ["حجزي مش قابل للاسترداد. ينفع ألغيه برضه؟", "ثانية أشوف. رقم الحجز كام واسم العيلة اللي عليه؟", "{BID}، {LAST}.",
 "الحجز {BID} {TYPE} من {CI} لـ {CO} بالسعر اللي مش بيترد، ومدفوع كله {TOTAL} جنيه. ينفع يتلغي بس الفلوس مش هترجع، ومينفعش تغير تواريخه كمان. لسه عايز تلغي؟",
 "لأ، خلاص هسيبه.", "تمام، الحجز {BID} فاضل مأكد. مستنيينك يوم {CI}."],
}
T['PAY_F1_status'] = {
'English': ["Has my payment gone through?", "Let me check. What is the booking reference and the last name on the booking?", "{BID}, {LAST}.",
 {'paid': "Yes — booking {BID} is paid in full: {PAID} EGP.",
  'pending': "Booking {BID} is on the Flexible rate and nothing has been charged yet: the stay of {TOTAL} EGP is paid at the hotel, at check-in or check-out."},
 "Great, thanks.", "You're welcome."],
'Arabic': ["هل تمت عملية الدفع؟", "دعني أتحقق. ما رقم الحجز واسم العائلة المسجل فيه؟", "{BID}، {LAST}.",
 {'paid': "نعم، الحجز {BID} مدفوع بالكامل: {PAID} جنيه مصري.",
  'pending': "الحجز {BID} بالسعر المرن ولم يُخصم أي مبلغ بعد، وتُدفع الإقامة البالغة {TOTAL} جنيه مصري في الفندق عند الوصول أو المغادرة."},
 "ممتاز، شكراً.", "على الرحب والسعة."],
'French': ["Mon paiement est-il passé ?", "Je vérifie. Quel est le numéro de réservation et le nom de famille de la réservation ?", "{BID}, {LAST}.",
 {'paid': "Oui — la réservation {BID} est payée intégralement : {PAID} EGP.",
  'pending': "La réservation {BID} est au tarif flexible et rien n'a encore été débité : le séjour de {TOTAL} EGP se paie à l'hôtel, à l'arrivée ou au départ."},
 "Parfait, merci.", "Je vous en prie."],
'Russian': ["Моя оплата прошла?", "Сейчас проверю. Какой номер брони и фамилия в ней?", "{BID}, фамилия {LAST}.",
 {'paid': "Да — бронь {BID} оплачена полностью: {PAID} EGP.",
  'pending': "Бронь {BID} по гибкому тарифу, пока ничего не списано: проживание стоимостью {TOTAL} EGP оплачивается в отеле при заезде или выезде."},
 "Отлично, спасибо.", "Пожалуйста."],
'Arabic-Egyptian': ["الدفع بتاعي عدّى؟", "ثانية أشوف. رقم الحجز كام واسم العيلة اللي عليه؟", "{BID}، {LAST}.",
 {'paid': "أيوة، الحجز {BID} مدفوع كله: {PAID} جنيه.",
  'pending': "الحجز {BID} بالسعر المرن ولسه مااتخصمش حاجة، والإقامة وقيمتها {TOTAL} جنيه بتتدفع في الفندق وقت الدخول أو الخروج."},
 "حلو، شكراً.", "العفو."],
}
T['PAY_F2_declined'] = {
'English': ["My card was declined when I tried to pay.", "Sorry about that. What is the booking reference and the last name on the booking?", "{BID}, {LAST}. Is my room still held?",
 "Booking {BID} is still confirmed — a {TYPE} from {CI} to {CO} on the Flexible rate, which is paid at the hotel, so the declined attempt does not cancel it. You can pay at check-in with another card, cash, Apple Pay, Vodafone Cash or InstaPay. For your security, never send card details by chat or phone; they are entered only on the secure payment page or at reception.",
 "Okay, that works.", "Great. We look forward to welcoming you on {CI}."],
'Arabic': ["رُفضت بطاقتي عندما حاولت الدفع.", "نأسف لذلك. ما رقم الحجز واسم العائلة المسجل فيه؟", "{BID}، {LAST}. هل ما زالت غرفتي محجوزة؟",
 "الحجز {BID} ما زال مؤكداً، وهو {TYPE} من {CI} إلى {CO} بالسعر المرن الذي يُدفع في الفندق، لذا لا تلغيه محاولة الدفع المرفوضة. يمكنك الدفع عند الوصول ببطاقة أخرى أو نقداً أو عبر Apple Pay أو Vodafone Cash أو InstaPay. وحفاظاً على أمانك، لا ترسل بيانات البطاقة عبر المحادثة أو الهاتف، فهي تُدخَل فقط في صفحة الدفع الآمنة أو في الاستقبال.",
 "حسناً، هذا مناسب.", "ممتاز. نتطلع إلى استقبالك يوم {CI}."],
'French': ["Ma carte a été refusée quand j'ai essayé de payer.", "Désolé. Quel est le numéro de réservation et le nom de famille de la réservation ?", "{BID}, {LAST}. Ma chambre est-elle toujours réservée ?",
 "La réservation {BID} est toujours confirmée — une {TYPE} du {CI} au {CO} au tarif flexible, payable à l'hôtel, donc le paiement refusé ne l'annule pas. Vous pourrez payer à l'arrivée avec une autre carte, en espèces, par Apple Pay, Vodafone Cash ou InstaPay. Pour votre sécurité, n'envoyez jamais vos données de carte par chat ou par téléphone : elles se saisissent uniquement sur la page de paiement sécurisée ou à la réception.",
 "D'accord, ça me va.", "Parfait. Nous vous attendons le {CI}."],
'Russian': ["Мою карту отклонили при оплате.", "Сожалеем. Какой номер брони и фамилия в ней?", "{BID}, {LAST}. Номер всё ещё за мной?",
 "Бронь {BID} по-прежнему подтверждена — {TYPE}, с {CI} по {CO}, гибкий тариф с оплатой в отеле, поэтому отклонённый платёж её не отменяет. Оплатить можно при заселении другой картой, наличными, через Apple Pay, Vodafone Cash или InstaPay. В целях безопасности не отправляйте данные карты в чате или по телефону — их вводят только на защищённой странице оплаты или на стойке регистрации.",
 "Хорошо, подходит.", "Отлично. Ждём вас {CI}."],
'Arabic-Egyptian': ["الكارت اترفض وأنا بدفع.", "آسفين على كده. رقم الحجز كام واسم العيلة اللي عليه؟", "{BID}، {LAST}. الأوضة لسه محجوزالي؟",
 "الحجز {BID} لسه مأكد، {TYPE} من {CI} لـ {CO} بالسعر المرن اللي بيتدفع في الفندق، فالكارت اللي اترفض مش بيلغيه. تقدر تدفع وقت الدخول بكارت تاني أو كاش أو Apple Pay أو فودافون كاش أو InstaPay. وعشان أمانك، ماتبعتش بيانات الكارت في الشات أو التليفون، دي بتتكتب بس في صفحة الدفع الآمنة أو في الاستقبال.",
 "تمام، كده ماشي.", "حلو. مستنيينك يوم {CI}."],
}
