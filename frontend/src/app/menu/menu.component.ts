import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MenuItem, MessageService, SharedModule } from 'primeng/api';
import { ButtonModule, ButtonSeverity } from 'primeng/button';
import { MenubarModule } from 'primeng/menubar';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { AuthService } from '../_services/auth.service';
import { HttpClient } from '@angular/common/http';

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
    private locationService: Location,
    private authService: AuthService,
    private http: HttpClient
  ) {

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
    } 
    else if (this.isNewUser) {
      this.register(this.userData);
    }
    else {
      this.authenticateUser(this.userData.email, this.userData.password);
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

  protected authenticateUser(email: string, password: string) {

    this.authService.login(email, password).subscribe({
      next: () => {
        this.router.navigate(['/submissions']).then(() => {
          this.messageService.add({
            severity: 'success',
            summary: 'Success.',
            detail: this.isNewUser ? 'Account created successfully.' : 'User logged in successfully.'
          });
        });
      },
      error: (err) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error.',
          detail: err.detail
        });
      }
    });

  }

  protected register(userData: any) {
    this.http.post('/api/register', userData).subscribe({
      next: () => {
        this.authenticateUser(userData.email, userData.password);
      },
      error: (err) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error.',
          detail: err.detail
        });
      }
    })
  }

  protected logout() {

    this.authService.logout();

    this.router.navigate(['/']).then(() => {
      this.messageService.add({
        severity: 'success',
        summary: 'Success.',
        detail: 'User logged out successfully.'
      });
    })

  }

}
