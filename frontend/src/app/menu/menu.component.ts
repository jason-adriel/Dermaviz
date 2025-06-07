import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MenuItem, MessageService, SharedModule } from 'primeng/api';
import { ButtonModule, ButtonSeverity } from 'primeng/button';
import { MenubarModule } from 'primeng/menubar';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';

@Component({
  selector: 'app-menu',
  imports: [
    SharedModule,
    ButtonModule,
    MenubarModule,
    DialogModule,
    InputTextModule
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss'
})
export class MenuComponent {

  public menuItems: MenuItem[] = [];
  public isDarkMode: boolean = true;
  public isShowInfoDialog: boolean = false;
  public isShowUserSettingsDialog: boolean = false;

  @Input('btnLabel') btnLabel: string = "Login";
  @Input('userData') userData: any;
  @Input('isUserAuthenticated') isUserAuthenticated: boolean = false;
  @Input('isNewUser') isNewUser: boolean = false;
  @Input('isUsingBackButton') isUsingBackButton: boolean = false;
  @Output() btnClick = new EventEmitter<string>();

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private messageService: MessageService,
    private locationService: Location
  )
  {

  }

  ngOnInit(): void {
    if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      this.isDarkMode = false;
      this.toggleDarkMode();
    }
  }

  protected onClick() {

    if (this.isUsingBackButton) {
      this.locationService.back();
    }
    else if (this.isUserAuthenticated) {
      this.logout();
    } else {
      this.authenticateUser();
    }

    this.btnClick.emit();

  }

  protected showDialog() {
    if (this.isUserAuthenticated) {
      this.isShowUserSettingsDialog = true;
    } else {
      this.isShowInfoDialog = true;
    }
  }

  protected toggleDarkMode() {
    const element = document.querySelector('html');
    element?.classList.toggle('dark');
    this.isDarkMode = !this.isDarkMode;
  } 

  protected authenticateUser() {

    this.router.navigate(['/submissions']).then(() => {
      this.messageService.add({
        severity : 'success',
        summary: 'Success.',
        detail: this.isNewUser ? 'Account created successfully.' : 'User logged in successfully.'
      });
    });

  }

  protected logout() {

    this.router.navigate(['/']).then(() => {
      this.messageService.add({
        severity : 'success',
        summary: 'Success.',
        detail: 'User logged out successfully.'
      });
    })

  }
  
}
