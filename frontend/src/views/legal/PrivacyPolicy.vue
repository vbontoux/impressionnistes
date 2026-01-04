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
              <li><strong>Historical Race Results:</strong> Crew member names and race results are preserved indefinitely as part of the event's historical records</li>
              <li><strong>Payment Records:</strong> 7 years (legal requirement for financial records in France)</li>
              <li><strong>Registration Data:</strong> Typically not retained on the registration server for more than 1 year, except for historical results and club manager contact information as noted above</li>
            </ul>
            <p>After these periods, data will be securely deleted or anonymized, except for historical race results which are preserved for archival purposes.</p>
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
              We use cookies to improve your experience on our website. Essential cookies are required for the site to function.
              You can manage your cookie preferences using the cookie banner or the "Cookie Preferences" link in the footer.
            </p>
            <p>For more information, see our Cookie Policy (accessible via the cookie banner).</p>
          </section>

          <section>
            <h2>11. International Data Transfers</h2>
            <p>
              Your data is stored on AWS servers located in the European Union (EU region).
              Some third-party services (Stripe, AWS) may process data outside the EU with appropriate safeguards (Standard Contractual Clauses).
            </p>
          </section>

          <section>
            <h2>12. Children's Privacy</h2>
            <p>
              Our service is intended for rowing club managers (adults). However, we process data of junior rowers (ages 14-18) as part of crew registrations.
              Club managers are responsible for obtaining parental consent for junior participants.
            </p>
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
              Email: {{ contactEmail }}<br>
              Website: {{ eventWebsite }}
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
              <li><strong>Résultats historiques des courses :</strong> Les noms des membres d'équipage et les résultats des courses sont conservés indéfiniment dans le cadre des archives historiques de l'événement</li>
              <li><strong>Enregistrements de paiement :</strong> 7 ans (exigence légale pour les enregistrements financiers en France)</li>
              <li><strong>Données d'inscription :</strong> Généralement non conservées sur le serveur d'inscription pendant plus d'un an, à l'exception des résultats historiques et des coordonnées des responsables de club comme indiqué ci-dessus</li>
            </ul>
            <p>Après ces périodes, les données seront supprimées ou anonymisées de manière sécurisée, à l'exception des résultats historiques des courses qui sont conservés à des fins d'archivage.</p>
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
              Nous utilisons des cookies pour améliorer votre expérience sur notre site web. Les cookies essentiels sont requis pour le fonctionnement du site.
              Vous pouvez gérer vos préférences de cookies en utilisant la bannière de cookies ou le lien "Préférences des cookies" dans le pied de page.
            </p>
            <p>Pour plus d'informations, consultez notre Politique de cookies (accessible via la bannière de cookies).</p>
          </section>

          <section>
            <h2>11. Transferts internationaux de données</h2>
            <p>
              Vos données sont stockées sur des serveurs AWS situés dans l'Union européenne (région UE).
              Certains services tiers (Stripe, AWS) peuvent traiter des données en dehors de l'UE avec des garanties appropriées (Clauses contractuelles types).
            </p>
          </section>

          <section>
            <h2>12. Confidentialité des enfants</h2>
            <p>
              Notre service est destiné aux managers de clubs d'aviron (adultes). Cependant, nous traitons les données de rameurs juniors (âgés de 14 à 18 ans) dans le cadre des inscriptions d'équipage.
              Les managers de club sont responsables d'obtenir le consentement parental pour les participants juniors.
            </p>
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
              Email : {{ contactEmail }}<br>
              Site web : {{ eventWebsite }}
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
