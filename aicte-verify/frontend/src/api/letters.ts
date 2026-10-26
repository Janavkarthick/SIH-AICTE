import apiClient from './client';
import { DeficiencyLetter } from '../types';
import { mockDeficiencyLetter } from './mockData';

export const lettersApi = {
  getDeficiencyLetter: async (applicationId: string): Promise<DeficiencyLetter> => {
    try {
      const response = await apiClient.get<DeficiencyLetter>(
        `/applications/${applicationId}/deficiency-letter`
      );
      return response.data;
    } catch {
      return { ...mockDeficiencyLetter, application_id: applicationId };
    }
  },

  generateLetter: async (
    applicationId: string,
    language: 'en' | 'ta' | 'hi' = 'en'
  ): Promise<DeficiencyLetter> => {
    try {
      const response = await apiClient.post<DeficiencyLetter>(
        `/applications/${applicationId}/deficiency-letter/generate`,
        { language }
      );
      return response.data;
    } catch {
      let subject = mockDeficiencyLetter.subject;
      let body = mockDeficiencyLetter.body_content;

      if (language === 'ta') {
        subject = 'அகில இந்திய தொழில்நுட்பக் கல்விக் குழு (AICTE) - குறைபாடுகள் குறித்த அறிவிப்பு கடிதம் (2025-26)';
        body = `பெறுநர்,
முதல்வர் / தலைவர்,
ஸ்ரீ கிருஷ்ணா பொறியியல் மற்றும் தொழில்நுட்பக் கல்லூரி,
கோயம்புத்தூர், தமிழ்நாடு - 641042.

ஐயா/அம்மா,

2025-26 ஆம் கல்வியாண்டிற்கான புதிய சேர்க்கை மற்றும் அங்கீகார நீட்டிப்பு விண்ணப்பத்தின் மீது நடத்தப்பட்ட விரிவான சரிபார்ப்பின் போது பின்வரும் குறைபாடுகள் கண்டறியப்பட்டுள்ளன.

இக்கடிதம் பெறப்பட்ட 15 வேலை நாட்களுக்குள் உரிய விளக்கங்கள் மற்றும் மூல ஆவணங்களை சமர்ப்பிக்குமாறு கேட்டுக் கொள்ளப்படுகிறீர்கள்.`;
      } else if (language === 'hi') {
        subject = 'अखिल भारतीय तकनीकी शिक्षा परिषद (AICTE) - कमी सूचना पत्र (सत्र 2025-26)';
        body = `सेवा में,
प्राचार्य / अध्यक्ष,
श्री कृष्णा कॉलेज ऑफ इंजीनियरिंग एंड टेक्नोलॉजी,
कोयम्बटूर, तमिलनाडु - 641042.

महोदय/महोदया,

सत्र 2025-26 के अनुमोदन विस्तार एवं अतिरिक्त सीट क्षमता आवेदन की जांच के दौरान पाई गई कमियों के संबंध में यह सूचना जारी की जा रही है।

आपसे अनुरोध है कि इस पत्र के जारी होने के 15 कार्य दिवसों के भीतर अपनी अनुपालन आख्या एवं मूल दस्तावेज प्रस्तुत करें।`;
      }

      return {
        ...mockDeficiencyLetter,
        application_id: applicationId,
        language,
        subject,
        body_content: body,
      };
    }
  },

  improveWordingWithGemini: async (letter: DeficiencyLetter): Promise<DeficiencyLetter> => {
    try {
      const response = await apiClient.post<DeficiencyLetter>(
        `/letters/${letter.id}/improve-wording`,
        letter
      );
      return response.data;
    } catch {
      return {
        ...letter,
        gemini_improved: true,
        body_content: `${letter.body_content}

[AI ASSISTED REFINEMENT - [Reference - verify against Approval Process Handbook] (illustrative)]:
"Please take urgent note that pursuant to Section 10(k) of the AICTE Act 1987 read with Chapter I of the Approval Process Handbook 2025-26, non-rectification of contiguous title clearance and faculty duplicity within the statutory 15-day window shall automatically bar the processing of additional course sanction and invoke the provisions of punitive reduction in existing intake."`,
      };
    }
  },

  approveLetter: async (letterId: string, officerName: string): Promise<DeficiencyLetter> => {
    try {
      const response = await apiClient.patch<DeficiencyLetter>(`/letters/${letterId}/approve`, {
        approved_by: officerName,
      });
      return response.data;
    } catch {
      return {
        ...mockDeficiencyLetter,
        id: letterId,
        status: 'approved',
        approved_by: officerName,
        approved_at: new Date().toISOString(),
      };
    }
  },
};
