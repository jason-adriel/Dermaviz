import { Component, InputSignal, OnInit, ViewChild } from '@angular/core';
import { Table, TableModule } from 'primeng/table';
import { MenuComponent } from '../menu/menu.component';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { CommonModule, DatePipe } from '@angular/common';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BadgeModule } from 'primeng/badge';
import { AuthService } from '../_services/auth.service';
import { DialogModule } from 'primeng/dialog';
import { ImageModule } from 'primeng/image';

export interface Submission {
  id: string;
  name: string;
  status: string;
  submissionTime: string;
  elapsedTime: string | null;
}

@Component({
  selector: 'app-submissions',
  imports: [
    TableModule,
    MenuComponent,
    InputTextModule,
    ButtonModule,
    DatePipe,
    IconFieldModule,
    InputIconModule,
    BadgeModule,
    CommonModule,
    DialogModule,
    ImageModule
  ],
  templateUrl: './submissions.component.html',
  styleUrl: './submissions.component.scss'
})
export class SubmissionsComponent implements OnInit {

  @ViewChild('submissions') tableSubmissions!: Table;

  public rowData: any[] = [];
  public selectedData: any[] = [];
  public isDeleteButtonShown: boolean = false;
  public isShowDetailDialog: boolean = false;
  public prediction: string = "";
  public resultImage: string = "";


  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private messageService: MessageService,
    private http: HttpClient,
    private authService: AuthService
  )
  {

  }

  ngOnInit(): void {
    this.http.get<Submission[]>('/api/submissions').subscribe({
      next: (data) => {
        this.rowData = data;
      },
      error: (err: HttpErrorResponse) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error.',
          detail: err.error?.detail || err.message || 'An unexpected error occurred.'
        });
        this.authService.logout();
      }
    });
  }

  protected refresh() {
    this.ngOnInit();
  }

  protected statusSeverity(status: string): "info" | "success" | "warn" | "danger" | "secondary" | "contrast" {
    if (status === 'IN QUEUE') {
      return "contrast";
    } else if (status === 'PROCESSING') {
      return "info"
    } else if (status === 'DONE') {
      return "success"
    } else {
      return "danger"
    }
  }

  protected onRowSelectChange() {
    if (this.selectedData.length > 0) {
      this.isDeleteButtonShown = true;
    } else {
      this.isDeleteButtonShown = false;
    }
  }

  protected onGlobalFilter(event: Event) {
    const input = event.target as HTMLInputElement;
    this.tableSubmissions.filterGlobal(input.value, 'contains');
  } 

  protected viewResult(data: any) {
    
    this.http.get<Submission[]>(`/api/results/${data.resultId}`).subscribe({
      next: (data: any) => {
        this.prediction = data.prediction;
        this.resultImage = `data:image/png;base64,${data.image}`;
        this.isShowDetailDialog = true;
      },
      error: (err: HttpErrorResponse) => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error.',
          detail: err.error?.detail || err.message || 'An unexpected error occurred.'
        });
      }
    });

  }

  protected addSubmission() {
    this.router.navigate(['/input']);
  }

}
