<template>
  <div class="terms-conditions-page">
    <div class="terms-conditions-container">
      <header class="policy-header">
        <h1>{{ $t('legal.termsConditions') }}</h1>
        <p class="last-updated">{{ $t('legal.lastUpdated') }}: {{ lastUpdated }}</p>
      </header>

      <div class="policy-content">
        <!-- English Content -->
        <div v-if="$i18n.locale === 'en'" class="content-section">
          <section>
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing and using the Course des Impressionnistes registration system ("the Service"), you accept and agree to be bound by these Terms and Conditions.
              If you do not agree to these terms, you may not use the Service.
            </p>
          </section>

          <section>
            <h2>2. Service Description</h2>
            <p>
              The Service provides an online registration platform for the Course des Impressionnistes rowing competition organized by Rowing Club Paris Métropole (RCPM).
              The Service allows club managers to:
            </p>
            <ul>
              <li>Register crew members and create boat crews</li>
              <li>Select races and manage registrations</li>
              <li>Request boat rentals from RCPM</li>
              <li>Process payments for registrations and rentals</li>
              <li>Manage crew information and race assignments</li>
            </ul>
          </section>

          <section>
            <h2>3. User Accounts</h2>
            <p><strong>Account Creation:</strong> You must create an account to use the Service. You are responsible for:</p>
            <ul>
              <li>Providing accurate and complete information</li>
              <li>Maintaining the security of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us immediately of any unauthorized access</li>
            </ul>
            <p><strong>Account Eligibility:</strong> You must be at least 18 years old and authorized to act on behalf of your rowing club.</p>
          </section>

          <section>
            <h2>4. Registration Requirements</h2>
            <p><strong>Crew Member Information:</strong> You must provide accurate information for all crew members, including:</p>
            <ul>
              <li>Full name, date of birth, and gender</li>
              <li>Valid French Rowing Federation (FFA) license number</li>
              <li>Club affiliation</li>
            </ul>
            <p><strong>License Verification:</strong> You are responsible for ensuring all crew members have valid FFA licenses. Invalid licenses may result in disqualification.</p>
            <p><strong>Parental Consent:</strong> For junior participants (under 18), you must obtain parental consent before registration.</p>
          </section>

          <section>
            <h2>5. Payment Terms</h2>
            <p><strong>Registration Fees:</strong> Fees are charged per seat for boat registrations and per boat for rentals, as published on the website.</p>
            <p><strong>Payment Processing:</strong> Payments are processed securely through Stripe. We do not store credit card information.</p>
            <p><strong>Payment Deadline:</strong> All payments must be completed by the published deadline. Late payments will not be accepted.</p>
            <p><strong>No Refunds:</strong> All payments are final and non-refundable once processed, except as required by law.</p>
            <p><strong>RCPM Members:</strong> RCPM members receive free registration (rental fees still apply).</p>
          </section>

          <section>
            <h2>6. Cancellation and Modifications</h2>
            <p><strong>Before Payment:</strong> You may modify or delete registrations freely before payment.</p>
            <p><strong>After Payment:</strong> Paid registrations cannot be deleted. Modifications may be allowed at organizer discretion.</p>
            <p><strong>After Registration Closes:</strong> No modifications or cancellations are permitted after the registration deadline.</p>
            <p><strong>Forfeit:</strong> If you cannot participate, contact us immediately. No refunds will be provided.</p>
          </section>

          <section>
            <h2>7. Boat Rentals</h2>
            <p><strong>Availability:</strong> Boat rentals are subject to availability and confirmed by RCPM.</p>
            <p><strong>Priority:</strong> RCPM members receive priority for boat rentals during the priority period.</p>
            <p><strong>Rental Fees:</strong> Rental fees are in addition to registration fees and must be paid before the deadline.</p>
            <p><strong>Boat Condition:</strong> You are responsible for returning rental boats in the same condition. Damage fees may apply.</p>
          </section>

          <section>
            <h2>8. User Responsibilities</h2>
            <p>You agree to:</p>
            <ul>
              <li>Provide accurate and truthful information</li>
              <li>Comply with all applicable laws and regulations</li>
              <li>Respect the intellectual property rights of RCPM and third parties</li>
              <li>Not use the Service for any unlawful or fraudulent purpose</li>
              <li>Not attempt to gain unauthorized access to the Service or other users' accounts</li>
              <li>Not interfere with the proper functioning of the Service</li>
            </ul>
          </section>

          <section>
            <h2>9. Intellectual Property</h2>
            <p>
              All content, trademarks, logos, and intellectual property on the Service are owned by RCPM or its licensors.
              You may not copy, reproduce, distribute, or create derivative works without written permission.
            </p>
          </section>

          <section>
            <h2>10. Limitation of Liability</h2>
            <p><strong>Service Availability:</strong> We strive to maintain the Service but do not guarantee uninterrupted or error-free operation.</p>
            <p><strong>Data Loss:</strong> We are not liable for any loss of data or information due to technical failures.</p>
            <p><strong>Third-Party Services:</strong> We are not responsible for the actions or services of third parties (Stripe, AWS, etc.).</p>
            <p><strong>Maximum Liability:</strong> Our total liability is limited to the amount you paid for the Service in the past 12 months.</p>
            <p><strong>Exclusions:</strong> We are not liable for indirect, incidental, consequential, or punitive damages.</p>
          </section>

          <section>
            <h2>11. Indemnification</h2>
            <p>
              You agree to indemnify and hold harmless RCPM, its officers, directors, employees, and agents from any claims, damages, losses, or expenses
              arising from your use of the Service, violation of these Terms, or infringement of any rights of third parties.
            </p>
          </section>

          <section>
            <h2>12. Privacy and Data Protection</h2>
            <p>
              Your use of the Service is also governed by our Privacy Policy, which explains how we collect, use, and protect your personal data.
              By using the Service, you consent to our data practices as described in the Privacy Policy.
            </p>
            <p>
              <router-link to="/privacy-policy">View Privacy Policy</router-link>
            </p>
          </section>

          <section>
            <h2>13. Termination</h2>
            <p><strong>By You:</strong> You may terminate your account at any time through the account settings.</p>
            <p><strong>By Us:</strong> We may suspend or terminate your account if you violate these Terms or engage in fraudulent activity.</p>
            <p><strong>Effect of Termination:</strong> Upon termination, you lose access to the Service. Paid registrations remain valid for the event.</p>
          </section>

          <section>
            <h2>14. Dispute Resolution</h2>
            <p><strong>Governing Law:</strong> These Terms are governed by French law.</p>
            <p><strong>Jurisdiction:</strong> Any disputes shall be resolved in the courts of Paris, France.</p>
            <p><strong>Informal Resolution:</strong> We encourage you to contact us first to resolve any disputes informally.</p>
          </section>

          <section>
            <h2>15. Changes to Terms</h2>
            <p>
              We may update these Terms from time to time. We will notify you of significant changes by email or through the Service.
              Continued use of the Service after changes constitutes acceptance of the new Terms.
            </p>
          </section>

          <section>
            <h2>16. Severability</h2>
            <p>
              If any provision of these Terms is found to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.
            </p>
          </section>

          <section>
            <h2>17. Entire Agreement</h2>
            <p>
              These Terms, together with the Privacy Policy, constitute the entire agreement between you and RCPM regarding the Service.
            </p>
          </section>

          <section>
            <h2>18. Contact Information</h2>
            <p>
              If you have any questions about these Terms and Conditions, please contact us:
            </p>
            <p class="contact-info">
              <strong>Rowing Club Paris Métropole (RCPM)</strong><br>
              Course des Impressionnistes<br>
              Email: {{ contactEmail }}<br>
              Website: {{ eventWebsite }}
            </p>
          </section>
        </div>

        <!-- French Content -->
        <div v-else class="content-section">
          <section>
            <h2>1. Acceptation des conditions</h2>
            <p>
              En accédant et en utilisant le système d'inscription de la Course des Impressionnistes ("le Service"), vous acceptez et vous engagez à respecter ces Conditions générales.
              Si vous n'acceptez pas ces conditions, vous ne pouvez pas utiliser le Service.
            </p>
          </section>

          <section>
            <h2>2. Description du service</h2>
            <p>
              Le Service fournit une plateforme d'inscription en ligne pour la compétition d'aviron Course des Impressionnistes organisée par le Rowing Club Paris Métropole (RCPM).
              Le Service permet aux managers de club de :
            </p>
            <ul>
              <li>Inscrire des équipiers et créer des équipages</li>
              <li>Sélectionner des courses et gérer les inscriptions</li>
              <li>Demander des locations de bateaux auprès du RCPM</li>
              <li>Traiter les paiements pour les inscriptions et les locations</li>
              <li>Gérer les informations des équipiers et les attributions de courses</li>
            </ul>
          </section>

          <section>
            <h2>3. Comptes utilisateurs</h2>
            <p><strong>Création de compte :</strong> Vous devez créer un compte pour utiliser le Service. Vous êtes responsable de :</p>
            <ul>
              <li>Fournir des informations exactes et complètes</li>
              <li>Maintenir la sécurité de vos identifiants de compte</li>
              <li>Toutes les activités qui se produisent sous votre compte</li>
              <li>Nous informer immédiatement de tout accès non autorisé</li>
            </ul>
            <p><strong>Éligibilité du compte :</strong> Vous devez avoir au moins 18 ans et être autorisé à agir au nom de votre club d'aviron.</p>
          </section>

          <section>
            <h2>4. Exigences d'inscription</h2>
            <p><strong>Informations des équipiers :</strong> Vous devez fournir des informations exactes pour tous les équipiers, y compris :</p>
            <ul>
              <li>Nom complet, date de naissance et genre</li>
              <li>Numéro de licence valide de la Fédération Française d'Aviron (FFA)</li>
              <li>Affiliation au club</li>
            </ul>
            <p><strong>Vérification de licence :</strong> Vous êtes responsable de vous assurer que tous les équipiers ont des licences FFA valides. Les licences invalides peuvent entraîner une disqualification.</p>
            <p><strong>Consentement parental :</strong> Pour les participants juniors (moins de 18 ans), vous devez obtenir le consentement parental avant l'inscription.</p>
          </section>

          <section>
            <h2>5. Conditions de paiement</h2>
            <p><strong>Frais d'inscription :</strong> Les frais sont facturés par siège pour les inscriptions de bateaux et par bateau pour les locations, comme publié sur le site web.</p>
            <p><strong>Traitement des paiements :</strong> Les paiements sont traités de manière sécurisée via Stripe. Nous ne stockons pas les informations de carte de crédit.</p>
            <p><strong>Date limite de paiement :</strong> Tous les paiements doivent être effectués avant la date limite publiée. Les paiements tardifs ne seront pas acceptés.</p>
            <p><strong>Aucun remboursement :</strong> Tous les paiements sont définitifs et non remboursables une fois traités, sauf si la loi l'exige.</p>
            <p><strong>Membres RCPM :</strong> Les membres RCPM bénéficient d'une inscription gratuite (les frais de location s'appliquent toujours).</p>
          </section>

          <section>
            <h2>6. Annulation et modifications</h2>
            <p><strong>Avant le paiement :</strong> Vous pouvez modifier ou supprimer les inscriptions librement avant le paiement.</p>
            <p><strong>Après le paiement :</strong> Les inscriptions payées ne peuvent pas être supprimées. Les modifications peuvent être autorisées à la discrétion de l'organisateur.</p>
            <p><strong>Après la clôture des inscriptions :</strong> Aucune modification ou annulation n'est autorisée après la date limite d'inscription.</p>
            <p><strong>Forfait :</strong> Si vous ne pouvez pas participer, contactez-nous immédiatement. Aucun remboursement ne sera fourni.</p>
          </section>

          <section>
            <h2>7. Locations de bateaux</h2>
            <p><strong>Disponibilité :</strong> Les locations de bateaux sont soumises à disponibilité et confirmées par le RCPM.</p>
            <p><strong>Priorité :</strong> Les membres RCPM bénéficient d'une priorité pour les locations de bateaux pendant la période de priorité.</p>
            <p><strong>Frais de location :</strong> Les frais de location s'ajoutent aux frais d'inscription et doivent être payés avant la date limite.</p>
            <p><strong>État du bateau :</strong> Vous êtes responsable de restituer les bateaux loués dans le même état. Des frais de dommages peuvent s'appliquer.</p>
          </section>

          <section>
            <h2>8. Responsabilités de l'utilisateur</h2>
            <p>Vous acceptez de :</p>
            <ul>
              <li>Fournir des informations exactes et véridiques</li>
              <li>Respecter toutes les lois et réglementations applicables</li>
              <li>Respecter les droits de propriété intellectuelle du RCPM et des tiers</li>
              <li>Ne pas utiliser le Service à des fins illégales ou frauduleuses</li>
              <li>Ne pas tenter d'obtenir un accès non autorisé au Service ou aux comptes d'autres utilisateurs</li>
              <li>Ne pas interférer avec le bon fonctionnement du Service</li>
            </ul>
          </section>

          <section>
            <h2>9. Propriété intellectuelle</h2>
            <p>
              Tout le contenu, les marques, les logos et la propriété intellectuelle sur le Service appartiennent au RCPM ou à ses concédants de licence.
              Vous ne pouvez pas copier, reproduire, distribuer ou créer des œuvres dérivées sans autorisation écrite.
            </p>
          </section>

          <section>
            <h2>10. Limitation de responsabilité</h2>
            <p><strong>Disponibilité du service :</strong> Nous nous efforçons de maintenir le Service mais ne garantissons pas un fonctionnement ininterrompu ou sans erreur.</p>
            <p><strong>Perte de données :</strong> Nous ne sommes pas responsables de toute perte de données ou d'informations due à des défaillances techniques.</p>
            <p><strong>Services tiers :</strong> Nous ne sommes pas responsables des actions ou services de tiers (Stripe, AWS, etc.).</p>
            <p><strong>Responsabilité maximale :</strong> Notre responsabilité totale est limitée au montant que vous avez payé pour le Service au cours des 12 derniers mois.</p>
            <p><strong>Exclusions :</strong> Nous ne sommes pas responsables des dommages indirects, accessoires, consécutifs ou punitifs.</p>
          </section>

          <section>
            <h2>11. Indemnisation</h2>
            <p>
              Vous acceptez d'indemniser et de dégager de toute responsabilité le RCPM, ses dirigeants, administrateurs, employés et agents de toute réclamation, dommage, perte ou dépense
              découlant de votre utilisation du Service, de la violation de ces Conditions ou de la violation de tout droit de tiers.
            </p>
          </section>

          <section>
            <h2>12. Confidentialité et protection des données</h2>
            <p>
              Votre utilisation du Service est également régie par notre Politique de confidentialité, qui explique comment nous collectons, utilisons et protégeons vos données personnelles.
              En utilisant le Service, vous consentez à nos pratiques en matière de données telles que décrites dans la Politique de confidentialité.
            </p>
            <p>
              <router-link to="/privacy-policy">Voir la Politique de confidentialité</router-link>
            </p>
          </section>

          <section>
            <h2>13. Résiliation</h2>
            <p><strong>Par vous :</strong> Vous pouvez résilier votre compte à tout moment via les paramètres du compte.</p>
            <p><strong>Par nous :</strong> Nous pouvons suspendre ou résilier votre compte si vous violez ces Conditions ou vous engagez dans une activité frauduleuse.</p>
            <p><strong>Effet de la résiliation :</strong> Lors de la résiliation, vous perdez l'accès au Service. Les inscriptions payées restent valides pour l'événement.</p>
          </section>

          <section>
            <h2>14. Résolution des litiges</h2>
            <p><strong>Loi applicable :</strong> Ces Conditions sont régies par le droit français.</p>
            <p><strong>Juridiction :</strong> Tout litige sera résolu devant les tribunaux de Paris, France.</p>
            <p><strong>Résolution informelle :</strong> Nous vous encourageons à nous contacter d'abord pour résoudre tout litige de manière informelle.</p>
          </section>

          <section>
            <h2>15. Modifications des conditions</h2>
            <p>
              Nous pouvons mettre à jour ces Conditions de temps en temps. Nous vous informerons des changements importants par e-mail ou via le Service.
              L'utilisation continue du Service après les modifications constitue l'acceptation des nouvelles Conditions.
            </p>
          </section>

          <section>
            <h2>16. Divisibilité</h2>
            <p>
              Si une disposition de ces Conditions est jugée invalide ou inapplicable, les dispositions restantes resteront pleinement en vigueur.
            </p>
          </section>

          <section>
            <h2>17. Accord complet</h2>
            <p>
              Ces Conditions, ainsi que la Politique de confidentialité, constituent l'accord complet entre vous et le RCPM concernant le Service.
            </p>
          </section>

          <section>
            <h2>18. Informations de contact</h2>
            <p>
              Si vous avez des questions sur ces Conditions générales, veuillez nous contacter :
            </p>
            <p class="contact-info">
              <strong>Rowing Club Paris Métropole (RCPM)</strong><br>
              Course des Impressionnistes<br>
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
.terms-conditions-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 2rem 1rem;
}

.terms-conditions-container {
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
  .terms-conditions-page {
    padding: 1rem 0.5rem;
  }

  .terms-conditions-container {
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
  .terms-conditions-page {
    background-color: white;
    padding: 0;
  }

  .terms-conditions-container {
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
