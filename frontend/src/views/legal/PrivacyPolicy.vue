<template>
  <div class="privacy-policy-page">
    <div class="privacy-policy-container">
      <header class="policy-header">
        <h1>{{ $t('legal.privacyPolicy') }}</h1>
        <p class="last-updated">{{ $t('legal.lastUpdated') }}: {{ lastUpdated }}</p>
      </header>

      <div class="policy-content">
        <!-- English Content -->
        <div v-if="$i18n.locale === 'en'" class="content-section">
          <section>
            <h2>1. Data Controller</h2>
            <p>
              The data controller responsible for your personal data is:
            </p>
            <p class="contact-info">
              <strong>Rowing Club de Port Marly (RCPM)</strong><br>
              Course des Impressionnistes<br>
              12bis Rue de Paris<br>
              78560 Le Port-Marly<br>
              France<br>
              Email: {{ contactEmail }}<br>
              Website: {{ eventWebsite }}
            </p>
          </section>

          <section>
            <h2>2. Personal Data We Collect</h2>
            <p>We collect and process the following types of personal data:</p>
            <ul>
              <li><strong>Account Information:</strong> Email address, first name, last name, mobile phone number, club affiliation</li>
              <li><strong>Crew Member Information:</strong> Full name, date of birth, gender, rowing license number, club affiliation</li>
              <li><strong>Registration Data:</strong> Boat registrations, race selections, seat assignments, rental requests</li>
              <li><strong>Payment Information:</strong> Payment transaction details (processed securely by Stripe - we do not store credit card numbers)</li>
              <li><strong>Technical Data:</strong> IP address, browser type, device information, cookies</li>
              <li><strong>Consent Records:</strong> Records of your consent to this Privacy Policy and Terms & Conditions</li>
            </ul>
          </section>

          <section>
            <h2>3. Purpose of Data Collection</h2>
            <p>We process your personal data for the following purposes:</p>
            <ul>
              <li><strong>Event Registration:</strong> To register participants for the Course des Impressionnistes rowing competition</li>
              <li><strong>Race Management:</strong> To organize races, assign bow numbers, manage start times, and coordinate logistics</li>
              <li><strong>Results Publication:</strong> To publish race results and event programs</li>
              <li><strong>Payment Processing:</strong> To process registration fees and boat rental payments</li>
              <li><strong>Communication:</strong> To send important event updates, registration confirmations, and payment receipts</li>
              <li><strong>Legal Compliance:</strong> To comply with sports federation regulations and financial record-keeping requirements</li>
            </ul>
          </section>

          <section>
            <h2>4. Legal Basis for Processing</h2>
            <p>We process your personal data based on:</p>
            <ul>
              <li><strong>Consent (GDPR Article 6(1)(a)):</strong> You have given explicit consent for registration and data processing</li>
              <li><strong>Contract Performance (GDPR Article 6(1)(b)):</strong> Processing is necessary to fulfill the registration contract</li>
              <li><strong>Legitimate Interest (GDPR Article 6(1)(f)):</strong> Event organization, safety, and results publication</li>
              <li><strong>Legal Obligation (GDPR Article 6(1)(c)):</strong> Financial record-keeping and sports federation compliance</li>
            </ul>
          </section>

          <section>
            <h2>5. Data Retention</h2>
            <p>We retain your personal data for the following periods:</p>
            <ul>
              <li><strong>User Accounts:</strong> Generally deleted before reopening registration for the next edition (typically within 1 year). This ensures data freshness and avoids issues with obsolete information, forgotten passwords, or changed contact details.</li>
              <li><strong>Club Manager Contact Information:</strong> Retained year-to-year to send invitations for subsequent editions of the event</li>
              <li><strong>Historical Race Results:</strong> Crew member names and race results are retained for 50 years for sports archival purposes, in accordance with our legitimate interest in preserving the event's sporting heritage. You may request removal or anonymization of your name from historical results by contacting us with a justified reason. We will evaluate such requests on a case-by-case basis, balancing your privacy rights with the historical and sporting interest of the records.</li>
              <li><strong>Payment Records:</strong> 7 years (legal requirement for financial records in France)</li>
              <li><strong>Registration Data:</strong> Typically not retained on the registration server for more than 1 year, except for historical results and club manager contact information as noted above</li>
            </ul>
            <p>After these periods, data will be securely deleted or anonymized.</p>
          </section>

          <section>
            <h2>6. Data Sharing and Third Parties</h2>
            <p>We share your personal data with the following third parties:</p>
            <ul>
              <li><strong>Stripe:</strong> Payment processing service (PCI-DSS compliant)</li>
              <li><strong>Amazon Web Services (AWS):</strong> Cloud hosting and data storage (EU region)</li>
              <li><strong>Amazon SES:</strong> Email delivery service for transactional emails</li>
              <li><strong>French Rowing Federation (FFA):</strong> License verification and competition compliance</li>
              <li><strong>Event Timing Services:</strong> Race timing and results management (CrewTimer)</li>
            </ul>
            <p>We do not sell your personal data to third parties.</p>
          </section>

          <section>
            <h2>7. Your Rights Under GDPR</h2>
            <p>You have the following rights regarding your personal data:</p>
            <ul>
              <li><strong>Right to Access (Article 15):</strong> Request a copy of all your personal data</li>
              <li><strong>Right to Rectification (Article 16):</strong> Correct inaccurate or incomplete data</li>
              <li><strong>Right to Erasure (Article 17):</strong> Request deletion of your data ("right to be forgotten")</li>
              <li><strong>Right to Portability (Article 20):</strong> Receive your data in a machine-readable format</li>
              <li><strong>Right to Object (Article 21):</strong> Object to processing based on legitimate interest</li>
              <li><strong>Right to Restrict Processing (Article 18):</strong> Limit how we use your data</li>
              <li><strong>Right to Withdraw Consent (Article 7(3)):</strong> Withdraw consent at any time</li>
            </ul>
          </section>

          <section>
            <h2>8. How to Exercise Your Rights</h2>
            <p>To exercise any of your rights, please:</p>
            <ul>
              <li><strong>Data Export:</strong> Use the "Download my data" button in your account settings</li>
              <li><strong>Account Deletion:</strong> Use the "Delete my account" button in your account settings</li>
              <li><strong>Other Requests:</strong> Contact us at {{ contactEmail }}</li>
            </ul>
            <p>We will respond to your request within 30 days.</p>
          </section>

          <section>
            <h2>9. Data Security</h2>
            <p>We implement appropriate technical and organizational measures to protect your personal data:</p>
            <ul>
              <li>HTTPS encryption for all data transmission</li>
              <li>Industry-standard password hashing (bcrypt)</li>
              <li>AWS Cognito for secure authentication</li>
              <li>Access controls and audit logging</li>
              <li>Regular security updates and monitoring</li>
              <li>Data stored in secure AWS infrastructure (EU region)</li>
            </ul>
          </section>

          <section>
            <h2>10. Cookies</h2>
            <p>
              We use cookies to improve your experience on our website. Below are the types of cookies we use:
            </p>
            
            <h3>Essential Cookies (Required)</h3>
            <p>
              These cookies are strictly necessary for the website to function and cannot be disabled. They do not require your consent under GDPR.
            </p>
            <ul>
              <li><strong>Authentication cookies:</strong> To keep you logged in during your session (AWS Cognito)</li>
              <li><strong>Security cookies:</strong> To protect against cross-site request forgery (CSRF) attacks</li>
              <li><strong>Session cookies:</strong> To maintain your preferences during your visit</li>
            </ul>

            <h3>Functional Cookies (Optional)</h3>
            <p>
              These cookies enhance functionality and personalization but are not essential. They require your consent.
            </p>
            <ul>
              <li><strong>Language preference:</strong> To remember your language choice (French/English)</li>
              <li><strong>Cookie consent:</strong> To remember your cookie preferences</li>
            </ul>

            <h3>Analytics Cookies (Optional)</h3>
            <p>
              We do not currently use analytics or tracking cookies. If we implement analytics in the future, we will:
            </p>
            <ul>
              <li>Request your explicit consent before placing any analytics cookies</li>
              <li>Use privacy-friendly analytics tools with IP anonymization</li>
              <li>Allow you to opt-out at any time</li>
            </ul>

            <h3>Managing Your Cookie Preferences</h3>
            <p>
              You can manage your cookie preferences at any time:
            </p>
            <ul>
              <li>Use the cookie banner that appears on your first visit</li>
              <li>Click the "Cookie Preferences" link in the footer</li>
              <li>Configure your browser settings to block or delete cookies</li>
            </ul>
            <p>
              Note: Blocking essential cookies may prevent certain features of the website from functioning properly.
            </p>
          </section>

          <section>
            <h2>11. International Data Transfers</h2>
            <p>
              Your data is stored on AWS servers located in the European Union (EU region).
              Some third-party services (Stripe, AWS) may process data outside the EU with appropriate safeguards (Standard Contractual Clauses).
            </p>
          </section>

          <section>
            <h2>12. Children's Privacy and Parental Consent</h2>
            
            <h3>Age Requirements and Parental Responsibility</h3>
            <p>
              Our registration platform is intended for use by adult rowing club managers (18 years and older). However, we process personal data of minor rowers (under 18 years old) as part of crew registrations for the Course des Impressionnistes competition.
            </p>

            <h3>Categories of Minors</h3>
            <ul>
              <li><strong>Junior rowers (14-17 years):</strong> Eligible to participate in junior categories</li>
              <li><strong>Minors under 14 years:</strong> Not eligible to participate in this competition</li>
            </ul>

            <h3>How Parental Consent is Obtained</h3>
            <p>
              The rowing club manager registering a minor crew member is responsible for:
            </p>
            <ul>
              <li><strong>Obtaining written parental consent</strong> before registering the minor in our system</li>
              <li><strong>Informing parents</strong> about:
                <ul>
                  <li>The personal data collected (name, date of birth, gender, license number, club affiliation)</li>
                  <li>The purpose of data processing (event registration, race management, results publication)</li>
                  <li>The retention period (50 years for historical race results, with possibility of removal)</li>
                  <li>Parents' rights to access, rectify, or request deletion of their child's data</li>
                </ul>
              </li>
              <li><strong>Keeping proof of parental consent</strong> on file at the rowing club for verification purposes</li>
              <li><strong>Ensuring compliance</strong> with French Rowing Federation (FFA) regulations regarding minor participation</li>
            </ul>

            <h3>Data Collected for Minors</h3>
            <p>
              For minor crew members, we collect only the data strictly necessary for competition participation:
            </p>
            <ul>
              <li>Full name</li>
              <li>Date of birth (to verify age eligibility)</li>
              <li>Gender (for race category assignment)</li>
              <li>Rowing license number (for FFA compliance)</li>
              <li>Club affiliation</li>
            </ul>
            <p>
              We do <strong>not</strong> collect email addresses, phone numbers, or other contact information directly from minors.
            </p>

            <h3>Parental Rights</h3>
            <p>
              Parents or legal guardians of minor participants have the right to:
            </p>
            <ul>
              <li><strong>Access:</strong> Request a copy of all personal data we hold about their child</li>
              <li><strong>Rectification:</strong> Correct any inaccurate or incomplete data</li>
              <li><strong>Erasure:</strong> Request deletion of their child's data from our active registration system</li>
              <li><strong>Object to processing:</strong> Object to the processing of their child's data for specific purposes</li>
              <li><strong>Withdraw consent:</strong> Withdraw consent at any time (note: this may prevent participation in the event)</li>
              <li><strong>Request anonymization:</strong> Request that their child's name be anonymized in historical race results</li>
            </ul>

            <h3>How to Exercise Parental Rights</h3>
            <p>
              Parents or legal guardians can exercise their rights by:
            </p>
            <ol>
              <li><strong>Contacting their rowing club manager</strong> who registered the minor, or</li>
              <li><strong>Contacting us directly</strong> at {{ contactEmail }} with:
                <ul>
                  <li>The minor's full name and date of birth</li>
                  <li>Proof of parental authority (copy of ID and family record book or equivalent)</li>
                  <li>A clear description of the request (access, rectification, deletion, etc.)</li>
                </ul>
              </li>
            </ol>
            <p>
              We will respond to parental requests within <strong>30 days</strong> and may request additional verification to ensure the request comes from a legitimate parent or guardian.
            </p>

            <h3>Special Considerations for Historical Results</h3>
            <p>
              Race results containing minors' names are retained for 50 years for sports archival purposes. Parents may request:
            </p>
            <ul>
              <li><strong>Anonymization:</strong> Replacing the minor's full name with initials or a pseudonym in published results</li>
              <li><strong>Removal:</strong> Complete removal from historical records (evaluated case-by-case)</li>
            </ul>
            <p>
              Such requests will be evaluated balancing the child's privacy rights with the legitimate interest in preserving sporting heritage, in accordance with CNIL guidelines.
            </p>

            <h3>Club Manager Responsibilities</h3>
            <p>
              Rowing club managers who register minors acknowledge and accept responsibility for:
            </p>
            <ul>
              <li>Obtaining and documenting valid parental consent before registration</li>
              <li>Ensuring parents are fully informed about data processing</li>
              <li>Acting as intermediary for parental requests regarding minors' data</li>
              <li>Complying with all applicable laws and FFA regulations regarding minor participation</li>
            </ul>
          </section>

          <section>
            <h2>13. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of significant changes by email or through the website.
              The "Last Updated" date at the top of this page indicates when the policy was last revised.
            </p>
          </section>

          <section>
            <h2>14. Supervisory Authority</h2>
            <p>
              If you believe your data protection rights have been violated, you have the right to lodge a complaint with the French data protection authority:
            </p>
            <p class="contact-info">
              <strong>Commission Nationale de l'Informatique et des Libertés (CNIL)</strong><br>
              3 Place de Fontenoy<br>
              TSA 80715<br>
              75334 Paris Cedex 07<br>
              France<br>
              Website: <a href="https://www.cnil.fr" target="_blank" rel="noopener">www.cnil.fr</a>
            </p>
          </section>

          <section>
            <h2>15. Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy or how we handle your personal data, please contact us:
            </p>
            <p class="contact-info">
              <strong>By email:</strong> {{ contactEmail }}<br>
              <strong>By mail:</strong> Rowing Club de Port Marly (RCPM), Course des Impressionnistes, 12bis Rue de Paris, 78560 Le Port-Marly, France<br>
              <strong>Website:</strong> {{ eventWebsite }}
            </p>
          </section>
        </div>

        <!-- French Content -->
        <div v-else class="content-section">
          <section>
            <h2>1. Responsable du traitement</h2>
            <p>
              Le responsable du traitement de vos données personnelles est :
            </p>
            <p class="contact-info">
              <strong>Rowing Club de Port Marly (RCPM)</strong><br>
              Course des Impressionnistes<br>
              12bis Rue de Paris<br>
              78560 Le Port-Marly<br>
              France<br>
              Email : {{ contactEmail }}<br>
              Site web : {{ eventWebsite }}
            </p>
          </section>

          <section>
            <h2>2. Données personnelles collectées</h2>
            <p>Nous collectons et traitons les types de données personnelles suivants :</p>
            <ul>
              <li><strong>Informations de compte :</strong> Adresse e-mail, prénom, nom, numéro de téléphone mobile, club d'affiliation</li>
              <li><strong>Informations des équipiers :</strong> Nom complet, date de naissance, genre, numéro de licence d'aviron, club d'affiliation</li>
              <li><strong>Données d'inscription :</strong> Inscriptions de bateaux, sélections de courses, attributions de places, demandes de location</li>
              <li><strong>Informations de paiement :</strong> Détails des transactions de paiement (traités de manière sécurisée par Stripe - nous ne stockons pas les numéros de carte de crédit)</li>
              <li><strong>Données techniques :</strong> Adresse IP, type de navigateur, informations sur l'appareil, cookies</li>
              <li><strong>Enregistrements de consentement :</strong> Enregistrements de votre consentement à cette Politique de confidentialité et aux Conditions générales</li>
            </ul>
          </section>

          <section>
            <h2>3. Finalité de la collecte de données</h2>
            <p>Nous traitons vos données personnelles aux fins suivantes :</p>
            <ul>
              <li><strong>Inscription à l'événement :</strong> Pour inscrire les participants à la compétition d'aviron Course des Impressionnistes</li>
              <li><strong>Gestion des courses :</strong> Pour organiser les courses, attribuer les numéros de dossard, gérer les horaires de départ et coordonner la logistique</li>
              <li><strong>Publication des résultats :</strong> Pour publier les résultats des courses et les programmes de l'événement</li>
              <li><strong>Traitement des paiements :</strong> Pour traiter les frais d'inscription et les paiements de location de bateaux</li>
              <li><strong>Communication :</strong> Pour envoyer des mises à jour importantes sur l'événement, des confirmations d'inscription et des reçus de paiement</li>
              <li><strong>Conformité légale :</strong> Pour se conformer aux réglementations de la fédération sportive et aux exigences de tenue de registres financiers</li>
            </ul>
          </section>

          <section>
            <h2>4. Base légale du traitement</h2>
            <p>Nous traitons vos données personnelles sur la base de :</p>
            <ul>
              <li><strong>Consentement (RGPD Article 6(1)(a)) :</strong> Vous avez donné votre consentement explicite pour l'inscription et le traitement des données</li>
              <li><strong>Exécution du contrat (RGPD Article 6(1)(b)) :</strong> Le traitement est nécessaire pour exécuter le contrat d'inscription</li>
              <li><strong>Intérêt légitime (RGPD Article 6(1)(f)) :</strong> Organisation de l'événement, sécurité et publication des résultats</li>
              <li><strong>Obligation légale (RGPD Article 6(1)(c)) :</strong> Tenue de registres financiers et conformité à la fédération sportive</li>
            </ul>
          </section>

          <section>
            <h2>5. Conservation des données</h2>
            <p>Nous conservons vos données personnelles pendant les périodes suivantes :</p>
            <ul>
              <li><strong>Comptes utilisateurs :</strong> Généralement supprimés avant la réouverture des inscriptions pour l'édition suivante (typiquement dans un délai d'un an). Cela garantit la fraîcheur des données et évite les problèmes liés aux informations obsolètes, aux mots de passe oubliés ou aux coordonnées modifiées.</li>
              <li><strong>Coordonnées des responsables de club :</strong> Conservées d'une année sur l'autre pour envoyer les invitations aux éditions suivantes de l'événement</li>
              <li><strong>Résultats historiques des courses :</strong> Les noms des membres d'équipage et les résultats des courses sont conservés pendant 50 ans à des fins d'archivage sportif, conformément à notre intérêt légitime de préserver le patrimoine sportif de l'événement. Vous pouvez demander le retrait ou l'anonymisation de votre nom des résultats historiques en nous contactant avec un motif justifié. Nous évaluerons ces demandes au cas par cas, en équilibrant vos droits à la vie privée avec l'intérêt historique et sportif des archives.</li>
              <li><strong>Enregistrements de paiement :</strong> 7 ans (exigence légale pour les enregistrements financiers en France)</li>
              <li><strong>Données d'inscription :</strong> Généralement non conservées sur le serveur d'inscription pendant plus d'un an, à l'exception des résultats historiques et des coordonnées des responsables de club comme indiqué ci-dessus</li>
            </ul>
            <p>Après ces périodes, les données seront supprimées ou anonymisées de manière sécurisée.</p>
          </section>

          <section>
            <h2>6. Partage de données et tiers</h2>
            <p>Nous partageons vos données personnelles avec les tiers suivants :</p>
            <ul>
              <li><strong>Stripe :</strong> Service de traitement des paiements (conforme PCI-DSS)</li>
              <li><strong>Amazon Web Services (AWS) :</strong> Hébergement cloud et stockage de données (région UE)</li>
              <li><strong>Amazon SES :</strong> Service de livraison d'e-mails pour les e-mails transactionnels</li>
              <li><strong>Fédération Française d'Aviron (FFA) :</strong> Vérification des licences et conformité à la compétition</li>
              <li><strong>Services de chronométrage d'événements :</strong> Chronométrage des courses et gestion des résultats (CrewTimer)</li>
            </ul>
            <p>Nous ne vendons pas vos données personnelles à des tiers.</p>
          </section>

          <section>
            <h2>7. Vos droits en vertu du RGPD</h2>
            <p>Vous disposez des droits suivants concernant vos données personnelles :</p>
            <ul>
              <li><strong>Droit d'accès (Article 15) :</strong> Demander une copie de toutes vos données personnelles</li>
              <li><strong>Droit de rectification (Article 16) :</strong> Corriger les données inexactes ou incomplètes</li>
              <li><strong>Droit à l'effacement (Article 17) :</strong> Demander la suppression de vos données ("droit à l'oubli")</li>
              <li><strong>Droit à la portabilité (Article 20) :</strong> Recevoir vos données dans un format lisible par machine</li>
              <li><strong>Droit d'opposition (Article 21) :</strong> S'opposer au traitement basé sur l'intérêt légitime</li>
              <li><strong>Droit de limitation du traitement (Article 18) :</strong> Limiter la façon dont nous utilisons vos données</li>
              <li><strong>Droit de retirer le consentement (Article 7(3)) :</strong> Retirer le consentement à tout moment</li>
            </ul>
          </section>

          <section>
            <h2>8. Comment exercer vos droits</h2>
            <p>Pour exercer l'un de vos droits, veuillez :</p>
            <ul>
              <li><strong>Export de données :</strong> Utiliser le bouton "Télécharger mes données" dans les paramètres de votre compte</li>
              <li><strong>Suppression de compte :</strong> Utiliser le bouton "Supprimer mon compte" dans les paramètres de votre compte</li>
              <li><strong>Autres demandes :</strong> Nous contacter à {{ contactEmail }}</li>
            </ul>
            <p>Nous répondrons à votre demande dans un délai de 30 jours.</p>
          </section>

          <section>
            <h2>9. Sécurité des données</h2>
            <p>Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour protéger vos données personnelles :</p>
            <ul>
              <li>Chiffrement HTTPS pour toutes les transmissions de données</li>
              <li>Hachage de mot de passe standard de l'industrie (bcrypt)</li>
              <li>AWS Cognito pour une authentification sécurisée</li>
              <li>Contrôles d'accès et journalisation d'audit</li>
              <li>Mises à jour de sécurité et surveillance régulières</li>
              <li>Données stockées dans une infrastructure AWS sécurisée (région UE)</li>
            </ul>
          </section>

          <section>
            <h2>10. Cookies</h2>
            <p>
              Nous utilisons des cookies pour améliorer votre expérience sur notre site web. Voici les types de cookies que nous utilisons :
            </p>
            
            <h3>Cookies essentiels (obligatoires)</h3>
            <p>
              Ces cookies sont strictement nécessaires au fonctionnement du site web et ne peuvent pas être désactivés. Ils ne nécessitent pas votre consentement en vertu du RGPD.
            </p>
            <ul>
              <li><strong>Cookies d'authentification :</strong> Pour vous maintenir connecté pendant votre session (AWS Cognito)</li>
              <li><strong>Cookies de sécurité :</strong> Pour protéger contre les attaques de type cross-site request forgery (CSRF)</li>
              <li><strong>Cookies de session :</strong> Pour maintenir vos préférences pendant votre visite</li>
            </ul>

            <h3>Cookies fonctionnels (optionnels)</h3>
            <p>
              Ces cookies améliorent les fonctionnalités et la personnalisation mais ne sont pas essentiels. Ils nécessitent votre consentement.
            </p>
            <ul>
              <li><strong>Préférence de langue :</strong> Pour mémoriser votre choix de langue (français/anglais)</li>
              <li><strong>Consentement aux cookies :</strong> Pour mémoriser vos préférences en matière de cookies</li>
            </ul>

            <h3>Cookies analytiques (optionnels)</h3>
            <p>
              Nous n'utilisons actuellement pas de cookies d'analyse ou de suivi. Si nous mettons en place des outils d'analyse à l'avenir, nous :
            </p>
            <ul>
              <li>Demanderons votre consentement explicite avant de placer des cookies analytiques</li>
              <li>Utiliserons des outils d'analyse respectueux de la vie privée avec anonymisation des adresses IP</li>
              <li>Vous permettrons de vous désinscrire à tout moment</li>
            </ul>

            <h3>Gestion de vos préférences en matière de cookies</h3>
            <p>
              Vous pouvez gérer vos préférences en matière de cookies à tout moment :
            </p>
            <ul>
              <li>Utiliser la bannière de cookies qui apparaît lors de votre première visite</li>
              <li>Cliquer sur le lien "Préférences des cookies" dans le pied de page</li>
              <li>Configurer les paramètres de votre navigateur pour bloquer ou supprimer les cookies</li>
            </ul>
            <p>
              Note : Le blocage des cookies essentiels peut empêcher certaines fonctionnalités du site web de fonctionner correctement.
            </p>
          </section>

          <section>
            <h2>11. Transferts internationaux de données</h2>
            <p>
              Vos données sont stockées sur des serveurs AWS situés dans l'Union européenne (région UE).
              Certains services tiers (Stripe, AWS) peuvent traiter des données en dehors de l'UE avec des garanties appropriées (Clauses contractuelles types).
            </p>
          </section>

          <section>
            <h2>12. Confidentialité des enfants et consentement parental</h2>
            
            <h3>Exigences d'âge et responsabilité parentale</h3>
            <p>
              Notre plateforme d'inscription est destinée à être utilisée par des responsables de clubs d'aviron adultes (18 ans et plus). Cependant, nous traitons les données personnelles de rameurs mineurs (moins de 18 ans) dans le cadre des inscriptions d'équipage pour la compétition Course des Impressionnistes.
            </p>

            <h3>Catégories de mineurs</h3>
            <ul>
              <li><strong>Rameurs juniors (14-17 ans) :</strong> Éligibles pour participer aux catégories juniors</li>
              <li><strong>Mineurs de moins de 14 ans :</strong> Non éligibles pour participer à cette compétition</li>
            </ul>

            <h3>Comment le consentement parental est obtenu</h3>
            <p>
              Le responsable du club d'aviron qui inscrit un membre d'équipage mineur est responsable de :
            </p>
            <ul>
              <li><strong>Obtenir le consentement parental écrit</strong> avant d'inscrire le mineur dans notre système</li>
              <li><strong>Informer les parents</strong> sur :
                <ul>
                  <li>Les données personnelles collectées (nom, date de naissance, genre, numéro de licence, club d'affiliation)</li>
                  <li>La finalité du traitement des données (inscription à l'événement, gestion des courses, publication des résultats)</li>
                  <li>La durée de conservation (50 ans pour les résultats historiques, avec possibilité de retrait)</li>
                  <li>Les droits des parents d'accéder, rectifier ou demander la suppression des données de leur enfant</li>
                </ul>
              </li>
              <li><strong>Conserver la preuve du consentement parental</strong> dans les dossiers du club d'aviron à des fins de vérification</li>
              <li><strong>Assurer la conformité</strong> avec les réglementations de la Fédération Française d'Aviron (FFA) concernant la participation des mineurs</li>
            </ul>

            <h3>Données collectées pour les mineurs</h3>
            <p>
              Pour les membres d'équipage mineurs, nous collectons uniquement les données strictement nécessaires à la participation à la compétition :
            </p>
            <ul>
              <li>Nom complet</li>
              <li>Date de naissance (pour vérifier l'éligibilité d'âge)</li>
              <li>Genre (pour l'attribution de catégorie de course)</li>
              <li>Numéro de licence d'aviron (pour la conformité FFA)</li>
              <li>Club d'affiliation</li>
            </ul>
            <p>
              Nous ne collectons <strong>pas</strong> d'adresses e-mail, de numéros de téléphone ou d'autres informations de contact directement auprès des mineurs.
            </p>

            <h3>Droits des parents</h3>
            <p>
              Les parents ou tuteurs légaux des participants mineurs ont le droit de :
            </p>
            <ul>
              <li><strong>Accès :</strong> Demander une copie de toutes les données personnelles que nous détenons sur leur enfant</li>
              <li><strong>Rectification :</strong> Corriger toute donnée inexacte ou incomplète</li>
              <li><strong>Effacement :</strong> Demander la suppression des données de leur enfant de notre système d'inscription actif</li>
              <li><strong>Opposition au traitement :</strong> S'opposer au traitement des données de leur enfant à des fins spécifiques</li>
              <li><strong>Retrait du consentement :</strong> Retirer le consentement à tout moment (note : cela peut empêcher la participation à l'événement)</li>
              <li><strong>Demande d'anonymisation :</strong> Demander que le nom de leur enfant soit anonymisé dans les résultats historiques des courses</li>
            </ul>

            <h3>Comment exercer les droits parentaux</h3>
            <p>
              Les parents ou tuteurs légaux peuvent exercer leurs droits en :
            </p>
            <ol>
              <li><strong>Contactant le responsable de leur club d'aviron</strong> qui a inscrit le mineur, ou</li>
              <li><strong>Nous contactant directement</strong> à {{ contactEmail }} avec :
                <ul>
                  <li>Le nom complet et la date de naissance du mineur</li>
                  <li>Une preuve de l'autorité parentale (copie de la pièce d'identité et du livret de famille ou équivalent)</li>
                  <li>Une description claire de la demande (accès, rectification, suppression, etc.)</li>
                </ul>
              </li>
            </ol>
            <p>
              Nous répondrons aux demandes parentales dans un délai de <strong>30 jours</strong> et pourrons demander une vérification supplémentaire pour nous assurer que la demande provient d'un parent ou tuteur légitime.
            </p>

            <h3>Considérations spéciales pour les résultats historiques</h3>
            <p>
              Les résultats de course contenant les noms de mineurs sont conservés pendant 50 ans à des fins d'archivage sportif. Les parents peuvent demander :
            </p>
            <ul>
              <li><strong>Anonymisation :</strong> Remplacement du nom complet du mineur par des initiales ou un pseudonyme dans les résultats publiés</li>
              <li><strong>Retrait :</strong> Suppression complète des archives historiques (évalué au cas par cas)</li>
            </ul>
            <p>
              Ces demandes seront évaluées en équilibrant les droits à la vie privée de l'enfant avec l'intérêt légitime de préserver le patrimoine sportif, conformément aux directives de la CNIL.
            </p>

            <h3>Responsabilités des responsables de club</h3>
            <p>
              Les responsables de clubs d'aviron qui inscrivent des mineurs reconnaissent et acceptent la responsabilité de :
            </p>
            <ul>
              <li>Obtenir et documenter un consentement parental valide avant l'inscription</li>
              <li>S'assurer que les parents sont pleinement informés du traitement des données</li>
              <li>Agir en tant qu'intermédiaire pour les demandes parentales concernant les données des mineurs</li>
              <li>Se conformer à toutes les lois applicables et aux réglementations de la FFA concernant la participation des mineurs</li>
            </ul>
          </section>

          <section>
            <h2>13. Modifications de cette politique</h2>
            <p>
              Nous pouvons mettre à jour cette Politique de confidentialité de temps en temps. Nous vous informerons des changements importants par e-mail ou via le site web.
              La date "Dernière mise à jour" en haut de cette page indique quand la politique a été révisée pour la dernière fois.
            </p>
          </section>

          <section>
            <h2>14. Autorité de contrôle</h2>
            <p>
              Si vous pensez que vos droits en matière de protection des données ont été violés, vous avez le droit de déposer une plainte auprès de l'autorité française de protection des données :
            </p>
            <p class="contact-info">
              <strong>Commission Nationale de l'Informatique et des Libertés (CNIL)</strong><br>
              3 Place de Fontenoy<br>
              TSA 80715<br>
              75334 Paris Cedex 07<br>
              France<br>
              Site web : <a href="https://www.cnil.fr" target="_blank" rel="noopener">www.cnil.fr</a>
            </p>
          </section>

          <section>
            <h2>15. Nous contacter</h2>
            <p>
              Si vous avez des questions sur cette Politique de confidentialité ou sur la façon dont nous traitons vos données personnelles, veuillez nous contacter :
            </p>
            <p class="contact-info">
              <strong>Par email :</strong> {{ contactEmail }}<br>
              <strong>Par courrier :</strong> Rowing Club de Port Marly (RCPM), Course des Impressionnistes, 12bis Rue de Paris, 78560 Le Port-Marly, France<br>
              <strong>Site web :</strong> {{ eventWebsite }}
            </p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const lastUpdated = computed(() => {
  return '2025-01-02';
});

const contactEmail = computed(() => {
  return import.meta.env.VITE_CONTACT_EMAIL || 'impressionnistes@rcpm-aviron.fr';
});

const eventWebsite = computed(() => {
  return import.meta.env.VITE_EVENT_WEBSITE || 'https://www.rcpm-aviron.fr';
});
</script>

<style scoped>
.privacy-policy-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 2rem 1rem;
}

.privacy-policy-container {
  max-width: 900px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.policy-header {
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}

.policy-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.last-updated {
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

.policy-content {
  line-height: 1.8;
  color: #333;
}

.content-section section {
  margin-bottom: 2.5rem;
}

.content-section h2 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-top: 1rem;
}

.content-section p {
  margin-bottom: 1rem;
}

.content-section ul {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.content-section li {
  margin-bottom: 0.5rem;
}

.content-section strong {
  color: #2c3e50;
  font-weight: 600;
}

.contact-info {
  background-color: #f8f9fa;
  padding: 1rem;
  border-left: 4px solid #4CAF50;
  margin: 1rem 0;
}

.contact-info a {
  color: #4CAF50;
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
  .privacy-policy-page {
    padding: 1rem 0.5rem;
  }

  .privacy-policy-container {
    padding: 1.5rem 1rem;
    border-radius: 0;
  }

  .policy-header h1 {
    font-size: 1.5rem;
  }

  .content-section h2 {
    font-size: 1.25rem;
  }

  .content-section ul {
    margin-left: 1rem;
  }
}

/* Print Styles */
@media print {
  .privacy-policy-page {
    background-color: white;
    padding: 0;
  }

  .privacy-policy-container {
    box-shadow: none;
    max-width: 100%;
  }

  .policy-header {
    border-bottom: 2px solid #000;
  }

  .contact-info {
    background-color: transparent;
    border-left: 2px solid #000;
  }

  a {
    color: #000;
    text-decoration: underline;
  }
}
</style>
