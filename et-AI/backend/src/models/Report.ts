import mongoose, { Schema, Document } from 'mongoose';

export interface IFraudReport extends Document {
  victimId: string;
  victimName: string;
  phoneNumber?: string; // Maps to Scammer Phone Number
  upiId?: string;       // Maps to Scammer UPI ID
  bankAccount?: string; // Maps to Scammer Bank Account
  deviceFingerprint?: string;
  reportTimestamp: Date;
  
  // New Crime Report Form Fields
  victimPhone?: string;
  victimEmail?: string;
  city?: string;
  state?: string;
  country?: string;
  dateOfIncident?: Date;
  typeOfScam?: string;
  amountLost?: number;
  description?: string;
  evidenceUrl?: string;

  createdAt: Date;
  updatedAt: Date;
}

const FraudReportSchema: Schema = new Schema(
  {
    victimId: {
      type: String,
      required: [true, 'victimId is required'],
      trim: true,
      index: true
    },
    victimName: {
      type: String,
      required: [true, 'victimName is required'],
      trim: true
    },
    phoneNumber: {
      type: String,
      trim: true,
      default: ''
    },
    upiId: {
      type: String,
      trim: true,
      default: ''
    },
    bankAccount: {
      type: String,
      trim: true,
      default: ''
    },
    deviceFingerprint: {
      type: String,
      trim: true,
      default: ''
    },
    reportTimestamp: {
      type: Date,
      default: Date.now,
      required: [true, 'reportTimestamp is required']
    },

    // New Fields
    victimPhone: {
      type: String,
      trim: true,
      default: ''
    },
    victimEmail: {
      type: String,
      trim: true,
      default: ''
    },
    city: {
      type: String,
      trim: true,
      default: ''
    },
    state: {
      type: String,
      trim: true,
      default: ''
    },
    country: {
      type: String,
      trim: true,
      default: ''
    },
    dateOfIncident: {
      type: Date,
      default: Date.now
    },
    typeOfScam: {
      type: String,
      trim: true,
      default: ''
    },
    amountLost: {
      type: Number,
      default: 0
    },
    description: {
      type: String,
      trim: true,
      default: ''
    },
    evidenceUrl: {
      type: String,
      trim: true,
      default: ''
    }
  },
  {
    timestamps: true
  }
);

// Add compound or individual indexes for search optimization if required
FraudReportSchema.index({ phoneNumber: 1 });
FraudReportSchema.index({ upiId: 1 });

export const Report = mongoose.model<IFraudReport>('Report', FraudReportSchema);
