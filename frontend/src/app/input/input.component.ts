import { Component } from '@angular/core';
import { MenuItem, MessageService } from 'primeng/api';
import { StepsModule } from 'primeng/steps';
import { MenuComponent } from '../menu/menu.component';
import { ButtonModule } from 'primeng/button';
import { FileUpload } from 'primeng/fileupload';
import { CommonModule } from '@angular/common';
import { BadgeModule } from 'primeng/badge';
import { CardModule } from 'primeng/card';
import { FloatLabel } from 'primeng/floatlabel';
import { InputText } from 'primeng/inputtext';
import { FieldsetModule } from 'primeng/fieldset';
import { MultiSelectModule } from 'primeng/multiselect';
import { SelectModule } from 'primeng/select';
import { InputNumberModule } from 'primeng/inputnumber';

@Component({
  selector: 'app-input',
  imports: [
    StepsModule,
    MenuComponent,
    ButtonModule,
    FileUpload,
    BadgeModule,
    CommonModule,
    CardModule,
    FloatLabel,
    InputText,
    FieldsetModule,
    MultiSelectModule,
    SelectModule,
    InputNumberModule
  ],
  templateUrl: './input.component.html',
  styleUrl: './input.component.scss'
})
export class InputComponent {

  public image: string = "";
  public genderOptions: any[] = [
    {
      name: "Male",
      value: "FEMALE"
    },
    {
      name: "Female",
      value: "MALE"
    },
    {
      name: "Other - Unspecified",
      value: "OTHER_OR_UNSPECIFIED"
    }
  ];

  public textureOptions: any[] = [
    {
      name: "Raised or Bumpy",
      value: "RAISED_OR_BUMPY"
    },
    {
      name: "Flat",
      value: "FLAT"
    },
    {
      name: "Rough or Flaky",
      value: "ROUGH_OR_FLAKY"
    },
    {
      name: "Fluid Filled",
      value: "FLUID_FILLED"
    },
    {
      name: "Other - Unspecified",
      value: "TEXTURE_UNSPECIFIED"
    },
  ];

  public locationOptions: any[] = [
    {
      name: "Head or Neck",
      value: "HEAD_OR_NECK"
    },
    {
      name: "Arm",
      value: "ARM"
    },
    {
      name: "Palm",
      value: "PALM"
    },
    {
      name: "Back of Hand",
      value: "BACK_OF_HAND"
    },
    {
      name: "Torso Front",
      value: "TORSO_FRONT"
    },
    {
      name: "Torso Back",
      value: "TORSO_BACK"
    },
    {
      name: "Genitalia or Groin",
      value: "GENITALIA_OR_GROIN"
    },
    {
      name: "Buttocks",
      value: "BUTTOCKS"
    },
    {
      name: "Leg",
      value: "LEG"
    },
    {
      name: "Foot Top or Side",
      value: "FOOT_TOP_OR_SIDE"
    },
    {
      name: "Foot Sole",
      value: "FOOT_SOLE"
    },
    {
      name: "Other",
      value: "OTHER"
    }
  ];
  public symptomsOptions: any[] = [
    {
      name: "Bothersome Appearance",
      value: "BOTHERSOME_APPEARANCE"
    },
    {
      name: "Bleeding",
      value: "BLEEDING"
    },
    {
      name: "Increasing Size",
      value: "INCREASING_SIZE"
    },
    {
      name: "Darkening",
      value: "DARKENING"
    },
    {
      name: "Itching",
      value: "ITCHING"
    },
    {
      name: "Burning",
      value: "BURNING"
    },
    {
      name: "Pain",
      value: "PAIN"
    },
    {
      name: "No Relevant Experience",
      value: "NO_RELEVANT_EXPERIENCE"
    }
  ];

  public durationOptions: any[] = [
    {
      name: "One day",
      value: "ONE_DAY"
    },
    {
      name: "Less than one week",
      value: "LESS_THAN_ONE_WEEK"
    },
    {
      name: "One to four weeks",
      value: "ONE_TO_FOUR_WEEKS"
    },
    {
      name: "One to three months",
      value: "ONE_TO_THREE_MONTHS"
    },
    {
      name: "Three to twelve months",
      value: "THREE_TO_TWELVE_MONTHS"
    },
    {
      name: "More than one year",
      value: "MORE_THAN_ONE_YEAR"
    },
    {
      name: "More than five years",
      value: "MORE_THAN_FIVE_YEARS"
    },
    {
      name: "Since childhood",
      value: "SINCE_CHILDHOOD"
    },
    {
      name: "Unknown",
      value: "UNKNOWN"
    }
  ];

  protected uploadedFiles: any[] = [];

  constructor(private messageService: MessageService) {}

  protected addSubmission() {

  }

  protected showInfoDialog() {
    
  }

}
