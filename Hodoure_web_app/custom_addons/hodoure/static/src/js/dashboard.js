/** @odoo-module */

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class hodoureDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        
        this.state = useState({
            data: {
                students_count: 0,
                teachers_count: 0,
                messages_count: 0,
                classes_count: 0,
                recent_activities: [],
                students_per_class: [],
                monthly_activity: []
            },
            loading: true,
            lastUpdated: null
        });

        this.charts = {};

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.initializeCharts();
            this.updateLastRefreshTime();
        });
    }

    async loadDashboardData() {
        try {
            const data = await this.rpc("/web/dataset/call_kw", {
                model: "hodoure.dashboard",
                method: "get_dashboard_data",
                args: [],
                kwargs: {}
            });
            
            this.state.data = data;
            this.state.loading = false;
        } catch (error) {
            console.warn('RPC call failed, using mock data:', error);
            // Fallback avec des données simulées
            this.state.data = await this.getMockData();
            this.state.loading = false;
        }
    }

    async getMockData() {
        return {
            students_count: 150,
            teachers_count: 25,
            messages_count: 47,
            classes_count: 12,
            recent_activities: [
                {
                    title: 'New Student Registered',
                    description: 'John Smith joined Class A',
                    time: '2 minutes ago',
                    icon: 'fa fa-user-plus'
                },
                {
                    title: 'Assignment Submitted',
                    description: 'Math homework submitted by Class B',
                    time: '15 minutes ago',
                    icon: 'fa fa-file-text'
                },
                {
                    title: 'New Message',
                    description: 'Parent inquiry about school schedule',
                    time: '1 hour ago',
                    icon: 'fa fa-envelope'
                }
            ],
            students_per_class: [
                {class_name: 'Class A', student_count: 30},
                {class_name: 'Class B', student_count: 28},
                {class_name: 'Class C', student_count: 32},
                {class_name: 'Class D', student_count: 25},
                {class_name: 'Class E', student_count: 35},
            ],
            monthly_activity: [
                {month: 'Jan 2024', count: 120},
                {month: 'Feb 2024', count: 135},
                {month: 'Mar 2024', count: 150},
                {month: 'Apr 2024', count: 140},
                {month: 'May 2024', count: 160},
                {month: 'Jun 2024', count: 175}
            ]
        };
    }

    initializeCharts() {
        // Attendre que Chart.js soit disponible
        if (typeof Chart !== 'undefined') {
            setTimeout(() => {
                this.createStudentsChart();
                this.createActivityChart();
            }, 100);
        } else {
            this.loadChartJS().then(() => {
                this.createStudentsChart();
                this.createActivityChart();
            });
        }
    }

    async loadChartJS() {
        return new Promise((resolve, reject) => {
            if (typeof Chart !== 'undefined') {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    createStudentsChart() {
        const canvas = document.getElementById('studentsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.data.students_per_class || [];
        
        // Cacher le loader
        const loader = document.getElementById('studentsChartLoading');
        if (loader) loader.style.display = 'none';
        canvas.style.display = 'block';

        // Détruire le graphique existant
        if (this.charts.studentsChart) {
            this.charts.studentsChart.destroy();
        }

        this.charts.studentsChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(item => item.class_name),
                datasets: [{
                    data: data.map(item => item.student_count),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 2000
                }
            }
        });
    }

    createActivityChart() {
        const canvas = document.getElementById('activityChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.data.monthly_activity || [];

        // Cacher le loader
        const loader = document.getElementById('activityChartLoading');
        if (loader) loader.style.display = 'none';
        canvas.style.display = 'block';

        // Détruire le graphique existant
        if (this.charts.activityChart) {
            this.charts.activityChart.destroy();
        }

        this.charts.activityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.month),
                datasets: [{
                    label: 'Activities',
                    data: data.map(item => item.count),
                    borderColor: '#2E7D32',
                    backgroundColor: 'rgba(46, 125, 50, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#2E7D32',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0,0,0,0.1)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    async onViewDetails(ev) {
        const action = ev.target.dataset.action;
        const actionMap = {
            'view_students': 'hodoure.action_student_list',
            'view_teachers': 'hodoure.action_teacher_list',
            'view_messages': 'hodoure.action_message_list',
            'view_classes': 'hodoure.action_class_list'
        };

        if (actionMap[action]) {
            this.action.doAction(actionMap[action]);
        }
    }

    async onQuickAction(ev) {
        const action = ev.target.dataset.action;
        const actionMap = {
            'create_student': 'hodoure.action_create_student',
            'create_teacher': 'hodoure.action_create_teacher',
            'send_notification': 'hodoure.action_send_notification',
            'view_reports': 'hodoure.action_reports'
        };

        if (actionMap[action]) {
            this.action.doAction(actionMap[action]);
        }
    }

    async onRefreshDashboard(ev) {
        const btn = ev.target.closest('button');
        const icon = btn.querySelector('i');
        
        btn.disabled = true;
        icon.classList.add('fa-spin');
        
        try {
            await this.loadDashboardData();
            this.destroyCharts();
            this.initializeCharts();
            this.updateLastRefreshTime();
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
        } finally {
            setTimeout(() => {
                btn.disabled = false;
                icon.classList.remove('fa-spin');
            }, 1000);
        }
    }

    updateLastRefreshTime() {
        this.state.lastUpdated = new Date().toLocaleTimeString();
    }

    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }

    willUnmount() {
        this.destroyCharts();
    }
}

hodoureDashboard.template = "hodoure.Dashboard";

// Enregistrer l'action dans le registre
const actionRegistry = registry.category("actions");
actionRegistry.add("hodoure.dashboard", hodoureDashboard);

export default hodoureDashboard;