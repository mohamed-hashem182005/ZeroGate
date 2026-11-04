# 📸 الصور التوضيحية لمشروع ZeroGate

تم إنشاء جميع الصور تلقائياً من ملفات PDF و HTML الموجودة في المستودع لتسهيل الاطلاع السريع على التصميم المعماري.

---

## 🗂️ تنظيم المجلدات

```
docs/images/
├── diagrams/          ← 13 رسمة معمارية (من PDF بجودة عالية)
│   ├── 01-component-architecture.png
│   ├── 02-domain-model.png
│   ├── 03-logical-data-model.png
│   └── ... (باقي الرسومات)
│
└── pages/             ← 16 صفحة توثيقية (من HTML)
    ├── index.png
    ├── architecture.png
    ├── api.png
    └── ... (باقي الصفحات)
```

---

## 🎨 الرسومات المعمارية (13 رسمة)

### 📂 المسار: `docs/images/diagrams/`

| الرقم | اسم الملف | الوصف | الفريق المعني |
|------|-----------|--------|---------------|
| 01 | `01-component-architecture.png` | المعمارية العامة للنظام (5 مناطق: Employee, Web Apps, SSH, Control Plane, Protected Resources) | 🌟 **جميع الفرق** |
| 02 | `02-domain-model.png` | النموذج المنطقي (7 كيانات: User, Device, Credential, Session, Policy, Certificate, AuditEvent) | Backend, Database |
| 03 | `03-logical-data-model.png` | نموذج البيانات المنطقي (العلاقات بين الكيانات) | Database, Backend |
| 04 | `04-identity-schema.png` | مخطط جداول الهوية والأجهزة (Users, Credentials, Devices) | 🌟 **Database Team** |
| 05 | `05-access-schema.png` | مخطط جداول الوصول والتدقيق (Sessions, Policies, Certificates, Audit) | 🌟 **Database Team** |
| 06 | `06-passkey-login.png` | تدفق تسجيل الدخول بـ Passkey (WebAuthn ceremony) | 🌟 **Frontend, Backend, Security** |
| 07 | `07-ssh-certificate-issuance.png` | تدفق إصدار شهادة SSH قصيرة الأجل | 🌟 **Security, Networking** |
| 08 | `08-jit-approval.png` | تدفق طلب الموافقة الفورية (Just-in-Time) | Backend, Frontend |
| 09 | `09-session-kill.png` | تدفق إنهاء الجلسة الفوري عند ارتفاع المخاطر | Backend, Frontend |
| 10 | `10-policy-engine.png` | محرك القرارات (Policy Engine logic flow) | 🌟 **Backend Team** |
| 11 | `11-session-state.png` | آلة الحالة للجلسات (ACTIVE → STEP_UP → KILLED → EXPIRED) | Backend |
| 12 | `12-jit-request-state.png` | آلة الحالة لطلبات JIT (PENDING → APPROVED/DENIED) | Backend |
| 13 | `13-device-state.png` | آلة الحالة للأجهزة (ENROLLED → COMPLIANT → QUARANTINED → REVOKED) | Backend, Frontend |

---

## 📄 الصفحات التوثيقية (16 صفحة)

### 📂 المسار: `docs/images/pages/`

| اسم الملف | الوصف | الفريق المعني |
|-----------|--------|---------------|
| `index.png` | الصفحة الرئيسية - نظرة عامة على المشروع | 🌟 **جميع الفرق** |
| `architecture.png` | شرح المعمارية العامة (النص الكامل) | جميع الفرق |
| `requirements.png` | المتطلبات الوظيفية الكاملة (FR-01 إلى FR-XX) | جميع الفرق |
| `api.png` | شرح واجهات البرمجة ونقاط النهاية | Backend, Frontend |
| `domain-model.png` | شرح النموذج المنطقي (Domain Model) | Backend, Database |
| `data-model.png` | شرح نموذج البيانات | Backend, Database |
| `database-schema.png` | شرح مخطط قاعدة البيانات بالتفصيل | 🌟 **Database Team** |
| `flow-passkey.png` | شرح تدفق Passkey بالتفصيل | Frontend, Backend, Security |
| `flow-ssh-certificate.png` | شرح تدفق SSH Certificate بالتفصيل | Security, Networking |
| `flow-jit-approval.png` | شرح تدفق JIT Approval بالتفصيل | Backend, Frontend |
| `flow-session-kill.png` | شرح تدفق Session Kill بالتفصيل | Backend, Frontend |
| `policy-engine.png` | شرح محرك السياسات بالتفصيل | 🌟 **Backend Team** |
| `risk-scoring.png` | شرح محرك تقييم المخاطر + نموذج ML | 🌟 **Backend, AI Team** |
| `state-session.png` | شرح آلة حالة الجلسات | Backend |
| `state-jit.png` | شرح آلة حالة JIT | Backend |
| `state-device.png` | شرح آلة حالة الأجهزة | Backend, Frontend |

---

## 🎯 دليل سريع لكل فريق

### 🗄️ Database Team
**ابدأ بهذه الصور:**
1. `diagrams/04-identity-schema.png` — جداول Users, Credentials, Devices
2. `diagrams/05-access-schema.png` — جداول Sessions, Policies, Certificates, Audit
3. `diagrams/03-logical-data-model.png` — العلاقات بين الجداول
4. `pages/database-schema.png` — الشرح الكامل للمخطط

### 🔧 Backend & AI Team
**ابدأ بهذه الصور:**
1. `diagrams/01-component-architecture.png` — المعمارية العامة
2. `diagrams/10-policy-engine.png` — منطق محرك القرارات ⭐
3. `diagrams/06-passkey-login.png` — تدفق المصادقة
4. `pages/policy-engine.png` — الشرح الكامل
5. `pages/risk-scoring.png` — نموذج ML والإشارات ⭐

### 🎨 Frontend Team
**ابدأ بهذه الصور:**
1. `diagrams/06-passkey-login.png` — واجهة تسجيل الدخول ⭐
2. `diagrams/08-jit-approval.png` — واجهة طلب الموافقة
3. `diagrams/09-session-kill.png` — زر القطع الفوري
4. `diagrams/11-session-state.png` — حالات الجلسة
5. `pages/flow-passkey.png` — الشرح الكامل

### 🔐 Security & Hardware Team
**ابدأ بهذه الصور:**
1. `diagrams/06-passkey-login.png` — FIDO2 WebAuthn flow ⭐
2. `diagrams/07-ssh-certificate-issuance.png` — SSH CA flow ⭐
3. `pages/flow-ssh-certificate.png` — الشرح الكامل
4. `diagrams/05-access-schema.png` — Audit events table

### 🌐 Networking Team
**ابدأ بهذه الصور:**
1. `diagrams/01-component-architecture.png` — المعمارية الشبكية ⭐
2. `diagrams/07-ssh-certificate-issuance.png` — SSH flow
3. `pages/architecture.png` — الشرح الكامل

### 🤖 AI Team
**ابدأ بهذه الصور:**
1. `pages/risk-scoring.png` — نموذج ML والإشارات ⭐⭐⭐
2. `diagrams/10-policy-engine.png` — كيف يتكامل ML مع Policy Engine
3. `pages/policy-engine.png` — الشرح الكامل

---

## 💡 كيفية الاستخدام

### عرض الصور:
```bash
# على Windows
start docs/images/diagrams/01-component-architecture.png

# على Mac/Linux
open docs/images/diagrams/01-component-architecture.png
```

### في المتصفح:
افتح ملف `docs/images/diagrams/01-component-architecture.png` مباشرة في المتصفح

### في VS Code:
- اضغط `Ctrl+Shift+V` (Windows) أو `Cmd+Shift+V` (Mac) لمعاينة الصورة
- أو ببساطة انقر على الملف `.png`

---

## 📊 إحصائيات الملفات

| النوع | العدد | المجلد | الحجم الإجمالي |
|-------|------|--------|----------------|
| رسومات معمارية | 13 | `docs/images/diagrams/` | ~2.5 MB |
| صفحات توثيقية | 16 | `docs/images/pages/` | ~1.8 MB |
| **المجموع** | **29 صورة** | `docs/images/` | **~4.3 MB** |

---

## ⚠️ ملاحظات مهمة

1. ✅ **الصور بجودة عالية** — دقة 1920x1080 وأعلى
2. ✅ **محدثة تلقائياً** — تم إنشاؤها من المصادر الأصلية (PDF و HTML)
3. ⚠️ **للمرجع السريع فقط** — ارجع دائماً للملفات الأصلية للتفاصيل الدقيقة
4. 📱 **قابلة للمشاركة** — يمكن إرسالها عبر WhatsApp/Telegram للفريق

---

## 🔄 إعادة إنشاء الصور

إذا تم تحديث ملفات PDF أو HTML، يمكن إعادة إنشاء الصور بتشغيل:

```bash
# إعادة إنشاء صور الرسومات من PDF
python -c "..." # (السكربت موجود في الأعلى)

# إعادة إنشاء صور الصفحات من HTML
python -c "..." # (السكربت موجود في الأعلى)
```

أو استخدم السكربت `take_screenshots.py` (إذا كان playwright مثبتاً).

---

**تم الإنشاء:** 2026-11-05  
**المشروع:** ZeroGate - Zero Trust Access Broker  
**الإجمالي:** 29 صورة توضيحية جاهزة للاستخدام
