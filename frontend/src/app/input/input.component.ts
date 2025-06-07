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
  public textureOptions: any[] = [];

  public stepItems: MenuItem[] = [
    {
      label: 'Image',
    },
    {
      label: 'Anamnesis'
    },
    {
      label: 'Upload'
    }
  ];

  uploadedFiles: any[] = [];

  constructor(private messageService: MessageService) {}

  protected addSubmission() {

  }

  protected showInfoDialog() {
    
  }

}
