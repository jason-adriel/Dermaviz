import { Component, ViewChild } from '@angular/core';
import { MessageService, SharedModule } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { MenubarModule } from 'primeng/menubar';
import { MenuComponent } from "../menu/menu.component";
import { FloatLabelModule } from 'primeng/floatlabel';
import { CardModule } from 'primeng/card';
import { InputGroupModule } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { FormGroup, FormControl, ReactiveFormsModule, Validators, NgForm } from '@angular/forms';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { trigger, transition, style, animate } from '@angular/animations';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-landing',
  imports: [
    SharedModule,
    ButtonModule,
    MenubarModule,
    MenuComponent,
    ReactiveFormsModule,
    FloatLabelModule,
    CardModule,
    InputGroupModule,
    InputGroupAddonModule,
    InputTextModule,
    PasswordModule
  ],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.scss',
  animations: [
    trigger('flyIn', [
      transition(':enter', [
        style({ transform: 'translateY(10px)', opacity: 0 }),
        animate('300ms ease-in', style({ transform: 'translateY(0)', opacity: 1 })),
      ]),
    ])
  ]
})
export class LandingComponent {

  @ViewChild('formInput') formInput!: NgForm;

  public userForm = new FormGroup({
    email: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required)
  });

  public registerForm = new FormGroup({
    email: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required),
    firstName: new FormControl('', Validators.required),
    lastName: new FormControl('', Validators.required)
  });

  public isNewUser: boolean = true;

  constructor(
    private messageService: MessageService,
    private route: ActivatedRoute,
    private router: Router  
  )
  {

  }

  protected toggleIsNewUser() {
    this.isNewUser = !this.isNewUser;
  }

}
