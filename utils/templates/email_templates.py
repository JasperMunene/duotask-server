from .helpers import first_name

full_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/full_scpz7t.png"
favicon_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/logo_pjlj60.png"
def verification_email_template(name, token):
    name = first_name(name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Welcome Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Welcome to Duotasks, {name}
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Thank you for joining our community of skilled professionals and opportunity seekers
                    </p>
                </div>
                
                <!-- Verification Code Section -->
                <div style="background: #f8fffe; border: 2px solid #dcfce7; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 24px; font-size: 16px; color: #374151; font-weight: 500;">
                        To complete your registration, please use this verification code:
                    </p>
                    <div style="background: #00915a; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(76, 175, 80, 0.25);">
                        <span style="font-size: 32px; font-weight: 700; letter-spacing: 6px; font-family: 'Courier New', monospace;">
                            {token}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <p style="margin: 0; font-size: 14px; color: #92400e; font-weight: 500;">
                            This code expires in 30 minutes
                        </p>
                    </div>
                </div>
                
                <!-- Platform Benefits -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What you can do with duotasks:
                    </h3>
                    <div style="color: #4b5563; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• Connect with trusted local professionals</p>
                        <p style="margin: 0 0 8px;">• Post tasks and find skilled help nearby</p>
                        <p style="margin: 0 0 8px;">• Build your reputation in the community</p>
                        <p style="margin: 0;">• Experience fair pricing and secure payments</p>
                    </div>
                </div>
                
                <!-- Security Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0; font-size: 14px; color: #6b7280; line-height: 1.5;">
                        If you didn't create a duotasks account, you can safely ignore this email.<br>
                        For your security, never share this verification code with anyone.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{full_logo}" alt="duotasks" style="height: 50px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Community. ✨
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """


def password_recovery_email_template(name, token):
    name = first_name(name)
    return f"""
    <body>
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Security Alert Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Password Reset Request
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Hi {name}, we received a request to reset your duotasks password
                    </p>
                </div>
                
                <!-- Verification Code Section -->
                <div style="background: #fef2f2; border: 2px solid #fecaca; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 24px; font-size: 16px; color: #374151; font-weight: 500;">
                        Use this verification code to reset your password:
                    </p>
                    <div style="background: #E53935; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(229, 57, 53, 0.25);">
                        <span style="font-size: 32px; font-weight: 700; letter-spacing: 6px; font-family: 'Courier New', monospace;">
                            {token}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <p style="margin: 0; font-size: 14px; color: #92400e; font-weight: 500;">
                            This code expires in 15 minutes for your security
                        </p>
                    </div>
                </div>
                
                <!-- Security Steps -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Steps to secure your account:
                    </h3>
                    <div style="color: #4b5563; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• Enter the verification code above</p>
                        <p style="margin: 0 0 8px;">• Create a strong, unique password</p>
                        <p style="margin: 0 0 8px;">• Confirm your new password</p>
                        <p style="margin: 0;">• Sign in securely with new credentials</p>
                    </div>
                </div>
                
                <!-- Security Tips -->
                <div style="background: #ecfdf5; border: 1px solid #d1fae5; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h4 style="margin: 0 0 12px; font-size: 16px; color: #065f46; font-weight: 600;">
                        Creating a secure password:
                    </h4>
                    <div style="color: #047857; line-height: 1.6; font-size: 14px;">
                        <p style="margin: 0 0 6px;">• Use at least 8 characters with mixed case and numbers</p>
                        <p style="margin: 0 0 6px;">• Avoid personal information or common phrases</p>
                        <p style="margin: 0;">• Consider using a trusted password manager</p>
                    </div>
                </div>
                
                <!-- Security Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #991b1b; line-height: 1.5; font-weight: 500;">
                            Didn't request a password reset?<br>
                            Your account remains secure. You can safely ignore this email.<br>
                            Never share this verification code with anyone.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks Security Team
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Protecting your account and privacy
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #E53935; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #E53935; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

def wallet_topup_email_template(name, transaction_id, amount, timestamp, payment_method="mpesa"):
    name = first_name(name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Success Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Top-up Successful!
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Hi {name}, your wallet has been credited successfully
                    </p>
                </div>
                
                <!-- Transaction Details Section -->
                <div style="background: #f8fffe; border: 2px solid #dcfce7; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        Transaction Details
                    </h3>
                    
                    <!-- Amount Display -->
                    <div style="text-align: center; margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid #d1fae5;">
                        <p style="margin: 0 0 8px; font-size: 14px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px;">
                            Amount Credited
                        </p>
                        <div style="background: #00915a; color: white; padding: 16px 24px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(0, 145, 90, 0.25);">
                            <span style="font-size: 36px; font-weight: 700; font-family: 'Courier New', monospace;">
                                KES {amount:,.2f}
                            </span>
                        </div>
                    </div>
                    
                    <!-- Transaction Info Grid -->
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="font-weight: 500; color: #6b7280;">Transaction ID:</span>
                            <span style="font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{transaction_id}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="font-weight: 500; color: #6b7280;">Payment Method:</span>
                            <span style="font-weight: 600; color: #1f2937;">{payment_method}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="font-weight: 500; color: #6b7280;">Date & Time:</span>
                            <span style="font-weight: 600; color: #1f2937;">{timestamp}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 12px 0;">
                            <span style="font-weight: 500; color: #6b7280;">Status:</span>
                            <span style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 14px;">Completed</span>
                        </div>
                    </div>
                </div>
                
                <!-- What's Next Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What you can do now:
                    </h3>
                    <div style="color: #4b5563; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• Browse available tasks in your area</p>
                        <p style="margin: 0 0 8px;">• Post your own tasks and hire professionals</p>
                        <p style="margin: 0 0 8px;">• Make secure payments for completed work</p>
                        <p style="margin: 0;">• Track your wallet balance anytime</p>
                    </div>
                </div>
                
                <!-- Security & Support Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #1e40af; line-height: 1.5; font-weight: 500;">
                            Questions about this transaction?<br>
                            Contact our support team anytime for assistance.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Your trusted community platform
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

from .helpers import first_name

full_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/full_scpz7t.png"
favicon_logo = "https://res.cloudinary.com/dfvauxrrg/image/upload/v1763130303/logo_pjlj60.png"

def wallet_authorization_email_template(name, amount, task_name, task_id, worker_name, worker_phone, worker_profile_image, timestamp):
    name = first_name(name)
    worker_first_name = first_name(worker_name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Authorization Notice Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: #fbbf24; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(251, 191, 36, 0.25);">
                        <span style="color: white; font-size: 40px;">🔒</span>
                    </div>
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Payment Authorized
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Hi {name}, funds have been reserved for your task
                    </p>
                </div>
                
                <!-- Amount Section -->
                <div style="background: #fffbeb; border: 2px solid #fde68a; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 16px; font-size: 16px; color: #92400e; font-weight: 500;">
                        Amount Authorized
                    </p>
                    <div style="background: #f59e0b; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(245, 158, 11, 0.25);">
                        <span style="font-size: 36px; font-weight: 700; font-family: 'Courier New', monospace;">
                            KES {amount:,.2f}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #dbeafe; border-radius: 8px; border-left: 4px solid #3b82f6;">
                        <p style="margin: 0; font-size: 14px; color: #1e40af; font-weight: 500;">
                            This amount is held securely until task completion
                        </p>
                    </div>
                </div>
                
                <!-- Task Details Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 20px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Task Details
                    </h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task Name</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{task_name}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task ID</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{task_id}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Agreed Amount</p>
                            <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 18px;">KES {amount:,.2f}</p>
                        </div>
                        <div style="padding: 12px 0;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Authorization Time</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{timestamp}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Worker Profile Section -->
                <div style="background: #f0fdfa; border: 2px solid #99f6e4; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        Your Task Worker
                    </h3>
                    
                    <!-- Worker Card -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <img src="{worker_profile_image}" alt="{worker_name}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 3px solid #00915a; margin-right: 20px;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px; font-size: 20px; color: #1f2937; font-weight: 600;">
                                    {worker_name}
                                </h4>
                                <div style="background: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; display: inline-block;">
                                    ASSIGNED
                                </div>
                            </div>
                        </div>
                        
                        <!-- Contact Info -->
                        <div style="background: #f9fafb; border-radius: 8px; padding: 16px;">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Contact Name</p>
                                <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{worker_name}</p>
                            </div>
                            <div>
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Phone Number</p>
                                <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 16px; font-family: 'Courier New', monospace;">
                                    📞 {worker_phone}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- What Happens Next Section -->
                <div style="background: #eff6ff; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What happens next:
                    </h3>
                    <div style="color: #1e40af; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">• {worker_first_name} will contact you to start the task</p>
                        <p style="margin: 0 0 8px;">• The authorized amount is safely held in escrow</p>
                        <p style="margin: 0 0 8px;">• Payment is released only after task completion</p>
                        <p style="margin: 0;">• You can review and confirm completion on your dashboard</p>
                    </div>
                </div>
                
                <!-- Important Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #fef3c7; border: 1px solid #fde68a; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #92400e; line-height: 1.5; font-weight: 500;">
                            💡 The authorized amount remains in your wallet but is reserved for this task.<br>
                            It will be transferred to {worker_first_name} once you confirm task completion.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Secure payments, trusted connections
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #f59e0b; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #f59e0b; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

def task_assignment_email_template(worker_name, amount, task_name, task_id, task_description, client_name, client_phone, client_profile_image, timestamp):
    worker_first_name = first_name(worker_name)
    client_first_name = first_name(client_name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Success Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: #00915a; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0, 145, 90, 0.25);">
                        <span style="color: white; font-size: 40px;">🎉</span>
                    </div>
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Congratulations, {worker_first_name}!
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        Your bid has been accepted and you've been assigned a task
                    </p>
                </div>
                
                <!-- Earning Amount Section -->
                <div style="background: #ecfdf5; border: 2px solid #a7f3d0; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 16px; font-size: 16px; color: #065f46; font-weight: 500;">
                        Your Earnings for This Task
                    </p>
                    <div style="background: #00915a; color: white; padding: 20px 32px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 16px rgba(0, 145, 90, 0.25);">
                        <span style="font-size: 36px; font-weight: 700; font-family: 'Courier New', monospace;">
                            KES {amount:,.2f}
                        </span>
                    </div>
                    <div style="margin-top: 24px; padding: 16px; background: #dbeafe; border-radius: 8px; border-left: 4px solid #3b82f6;">
                        <p style="margin: 0; font-size: 14px; color: #1e40af; font-weight: 500;">
                            💰 Funds are secured in escrow and will be released upon task completion
                        </p>
                    </div>
                </div>
                
                <!-- Task Details Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 20px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Task Details
                    </h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task Name</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{task_name}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task ID</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{task_id}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Description</p>
                            <p style="margin: 0; font-weight: 500; color: #374151; line-height: 1.6;">{task_description}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Your Payment</p>
                            <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 18px;">KES {amount:,.2f}</p>
                        </div>
                        <div style="padding: 12px 0;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Assignment Time</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{timestamp}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Client Profile Section -->
                <div style="background: #fef3c7; border: 2px solid #fde68a; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        Your Client
                    </h3>
                    
                    <!-- Client Card -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <img src="{client_profile_image}" alt="{client_name}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 3px solid #f59e0b; margin-right: 20px;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px; font-size: 20px; color: #1f2937; font-weight: 600;">
                                    {client_name}
                                </h4>
                                <div style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; display: inline-block;">
                                    TASK POSTER
                                </div>
                            </div>
                        </div>
                        
                        <!-- Contact Info -->
                        <div style="background: #f9fafb; border-radius: 8px; padding: 16px;">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Contact Name</p>
                                <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{client_name}</p>
                            </div>
                            <div>
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Phone Number</p>
                                <p style="margin: 0; font-weight: 600; color: #f59e0b; font-size: 16px; font-family: 'Courier New', monospace;">
                                    📞 {client_phone}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Next Steps Section -->
                <div style="background: #ecfdf5; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Your Next Steps:
                    </h3>
                    <div style="color: #065f46; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">✅ Contact {client_first_name} using the duotaks ap or phone number provided above if available </p>
                        <p style="margin: 0 0 8px;">✅ Confirm task details and schedule</p>
                        <p style="margin: 0 0 8px;">✅ Complete the task to the best of your ability</p>
                        <p style="margin: 0;">✅ Payment will be released to you once {client_first_name} confirms completion</p>
                    </div>
                </div>
                
                <!-- Important Tips -->
                <div style="background: #eff6ff; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        💡 Pro Tips for Success:
                    </h3>
                    <div style="color: #1e40af; line-height: 1.6; font-size: 14px;">
                        <p style="margin: 0 0 8px;">• Communicate promptly and professionally with {client_first_name}</p>
                        <p style="margin: 0 0 8px;">• Ask questions if anything is unclear before starting</p>
                        <p style="margin: 0 0 8px;">• Keep {client_first_name} updated on your progress</p>
                        <p style="margin: 0 0 8px;">• Take photos/documentation as proof of completion</p>
                        <p style="margin: 0;">• Deliver quality work to build your reputation and get more tasks</p>
                    </div>
                </div>
                
                <!-- Payment Security Notice -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #ecfdf5; border: 2px solid #a7f3d0; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #065f46; line-height: 1.5; font-weight: 500;">
                            🔒 Your payment of KES {amount:,.2f} is secured in escrow.<br>
                            Once {client_first_name} confirms task completion, funds will be instantly released to your wallet.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Earn money, build your reputation
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

def task_completion_email_template(client_name, worker_name, amount, task_name, task_id, task_description, worker_phone, worker_profile_image, completion_timestamp, review_link):
    client_first_name = first_name(client_name)
    worker_first_name = first_name(worker_name)
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Completion Notice Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: #00915a; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0, 145, 90, 0.25);">
                        <span style="color: white; font-size: 40px;">✅</span>
                    </div>
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Task Completed, {client_first_name}!
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        {worker_first_name} has marked your task as complete
                    </p>
                </div>
                
                <!-- Action Required Alert -->
                <div style="background: #fef3c7; border: 2px solid #fde68a; border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 32px;">
                    <p style="margin: 0 0 8px; font-size: 14px; color: #92400e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                        ⚠️ Action Required
                    </p>
                    <p style="margin: 0; font-size: 16px; color: #78350f; font-weight: 500; line-height: 1.5;">
                        Please review the work and confirm completion to release payment
                    </p>
                </div>
                
                <!-- Task Details Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 20px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        Task Details
                    </h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task Name</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{task_name}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task ID</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{task_id}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Description</p>
                            <p style="margin: 0; font-weight: 500; color: #374151; line-height: 1.6;">{task_description}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Payment Amount</p>
                            <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 18px;">KES {amount:,.2f}</p>
                        </div>
                        <div style="padding: 12px 0;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Completed At</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{completion_timestamp}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Worker Profile Section -->
                <div style="background: #ecfdf5; border: 2px solid #a7f3d0; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        Task Completed By
                    </h3>
                    
                    <!-- Worker Card -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <img src="{worker_profile_image}" alt="{worker_name}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 3px solid #00915a; margin-right: 20px;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0 0 8px; font-size: 20px; color: #1f2937; font-weight: 600;">
                                    {worker_name}
                                </h4>
                                <div style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; display: inline-block;">
                                    TASK DOER
                                </div>
                            </div>
                        </div>
                        
                        <!-- Contact Info -->
                        <div style="background: #f9fafb; border-radius: 8px; padding: 16px;">
                            <div style="margin-bottom: 12px;">
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Contact Name</p>
                                <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{worker_name}</p>
                            </div>
                            <div>
                                <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Phone Number</p>
                                <p style="margin: 0; font-weight: 600; color: #00915a; font-size: 16px; font-family: 'Courier New', monospace;">
                                    📞 {worker_phone}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Review & Settle CTA -->
                <div style="background: linear-gradient(135deg, #00915a 0%, #047857 100%); border-radius: 16px; padding: 40px; text-align: center; margin-bottom: 32px; box-shadow: 0 8px 24px rgba(0, 145, 90, 0.3);">
                    <h3 style="margin: 0 0 16px; font-size: 24px; color: #ffffff; font-weight: 700;">
                        Ready to Review & Settle?
                    </h3>
                    <p style="margin: 0 0 28px; font-size: 16px; color: #d1fae5; line-height: 1.5;">
                        Click the button below to review {worker_first_name}'s work and release the payment of KES {amount:,.2f}
                    </p>
                    <a href="{review_link}" style="display: inline-block; background: #ffffff; color: #00915a; padding: 18px 48px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 18px; box-shadow: 0 4px 16px rgba(0,0,0,0.2); transition: transform 0.2s;">
                        Review & Settle Task →
                    </a>
                    <p style="margin: 24px 0 0; font-size: 13px; color: #d1fae5;">
                        Or copy this link: <span style="word-break: break-all; font-family: 'Courier New', monospace;">{review_link}</span>
                    </p>
                </div>
                
                <!-- What Happens Next -->
                <div style="background: #eff6ff; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        What Happens Next:
                    </h3>
                    <div style="color: #1e40af; line-height: 1.6;">
                        <p style="margin: 0 0 8px;">1️⃣ Review the work completed by {worker_first_name}</p>
                        <p style="margin: 0 0 8px;">2️⃣ If satisfied, confirm completion to release payment</p>
                        <p style="margin: 0 0 8px;">3️⃣ Rate and review {worker_first_name}'s performance</p>
                        <p style="margin: 0;">4️⃣ The KES {amount:,.2f} will be instantly released from escrow to {worker_first_name}'s wallet</p>
                    </div>
                </div>
                
                <!-- Important Notice -->
                <div style="background: #fef2f2; border: 2px solid #fecaca; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #991b1b; font-weight: 600;">
                        ⚠️ Important Notice:
                    </h3>
                    <div style="color: #991b1b; line-height: 1.6; font-size: 14px;">
                        <p style="margin: 0 0 8px;">• If you're not satisfied with the work, please contact {worker_first_name} before confirming</p>
                        <p style="margin: 0 0 8px;">• Once you confirm completion, the payment will be immediately released</p>
                        <p style="margin: 0 0 8px;">• If there's a dispute, contact support@duotasks.net for assistance</p>
                        <p style="margin: 0;">• Your funds are safely held in escrow until you confirm</p>
                    </div>
                </div>
                
                <!-- Payment Details -->
                <div style="text-align: center; margin-bottom: 32px;">
                    <div style="background: #ecfdf5; border: 2px solid #a7f3d0; border-radius: 8px; padding: 20px;">
                        <p style="margin: 0; font-size: 14px; color: #065f46; line-height: 1.5; font-weight: 500;">
                            🔒 Payment of KES {amount:,.2f} is secured in escrow.<br>
                            It will only be released to {worker_first_name} after you confirm task completion.
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Connect. Complete. Compensate.
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

def payment_received_email_template(worker_name, agreed_amount, task_name, task_id, client_name, client_profile_image, completion_timestamp, settlement_timestamp):
    worker_first_name = first_name(worker_name)
    client_first_name = first_name(client_name)
    
    # Calculate fees and final payout
    service_fee = agreed_amount * 0.10
    final_payout = agreed_amount - service_fee
    
    return f"""
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; color: #1a1a1a; padding: 20px; margin: 0; min-height: 100vh;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden;">
            
            <!-- Header -->
            <div style="background: #ffffff; padding: 32px 40px 24px; text-align: center; border-bottom: 1px solid #f0f0f0;">
                <img src="{full_logo}" alt="duotasks" style="height: 150px; width: auto; margin-bottom: 8px;">
            </div>
            
            <!-- Main Content -->
            <div style="padding: 48px 40px;">
                <!-- Success Section -->
                <div style="text-align: center; margin-bottom: 40px;">
                    <div style="background: #00915a; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0, 145, 90, 0.25);">
                        <span style="color: white; font-size: 40px;">💰</span>
                    </div>
                    <h1 style="margin: 0 0 16px; font-size: 28px; font-weight: 600; color: #1a1a1a; line-height: 1.3;">
                        Payment Received, {worker_first_name}!
                    </h1>
                    <p style="margin: 0; font-size: 18px; color: #6b7280; line-height: 1.5;">
                        {client_first_name} confirmed task completion and your payment has been released
                    </p>
                </div>
                
                <!-- Payout Amount Section -->
                <div style="background: linear-gradient(135deg, #00915a 0%, #047857 100%); border-radius: 16px; padding: 40px; text-align: center; margin-bottom: 32px; box-shadow: 0 8px 24px rgba(0, 145, 90, 0.3);">
                    <p style="margin: 0 0 20px; font-size: 16px; color: #d1fae5; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                        Your Payout
                    </p>
                    <div style="background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); color: white; padding: 28px 40px; border-radius: 16px; display: inline-block; border: 2px solid rgba(255, 255, 255, 0.2);">
                        <span style="font-size: 48px; font-weight: 700; font-family: 'Courier New', monospace; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                            KES {final_payout:,.2f}
                        </span>
                    </div>
                    <p style="margin: 24px 0 0; font-size: 14px; color: #d1fae5;">
                        ✅ Funds have been credited to your duotasks wallet
                    </p>
                </div>
                
                <!-- Payment Breakdown Section -->
                <div style="background: #f9fafb; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 20px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        💳 Payment Breakdown
                    </h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="padding: 16px 0; border-bottom: 2px solid #e5e7eb;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p style="margin: 0 0 4px; font-size: 14px; color: #1f2937; font-weight: 600;">Task Payment</p>
                                    <p style="margin: 0; font-size: 12px; color: #6b7280;">Agreed amount with {client_first_name}</p>
                                </div>
                                <p style="margin: 0; font-weight: 700; color: #1f2937; font-size: 20px;">KES {agreed_amount:,.2f}</p>
                            </div>
                        </div>
                        <div style="padding: 16px 0; border-bottom: 2px solid #e5e7eb;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p style="margin: 0 0 4px; font-size: 14px; color: #dc2626; font-weight: 600;">duotasks Service Fee (10%)</p>
                                    <p style="margin: 0; font-size: 12px; color: #6b7280;">Platform maintenance & support</p>
                                </div>
                                <p style="margin: 0; font-weight: 700; color: #dc2626; font-size: 18px;">- KES {service_fee:,.2f}</p>
                            </div>
                        </div>
                        <div style="padding: 16px 0; background: #ecfdf5; margin: -24px -24px 0 -24px; padding: 24px; border-radius: 0 0 12px 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <p style="margin: 0 0 4px; font-size: 16px; color: #065f46; font-weight: 700;">Your Net Payout</p>
                                    <p style="margin: 0; font-size: 12px; color: #047857;">Amount credited to your wallet</p>
                                </div>
                                <p style="margin: 0; font-weight: 700; color: #00915a; font-size: 24px;">KES {final_payout:,.2f}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Task Details Section -->
                <div style="background: #eff6ff; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 20px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        📋 Task Details
                    </h3>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="padding: 12px 0; border-bottom: 1px solid #dbeafe;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task Name</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-size: 16px;">{task_name}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #dbeafe;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Task ID</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937; font-family: 'Courier New', monospace;">{task_id}</p>
                        </div>
                        <div style="padding: 12px 0; border-bottom: 1px solid #dbeafe;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Completed On</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{completion_timestamp}</p>
                        </div>
                        <div style="padding: 12px 0;">
                            <p style="margin: 0 0 4px; font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Payment Released On</p>
                            <p style="margin: 0; font-weight: 600; color: #1f2937;">{settlement_timestamp}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Client Profile Section -->
                <div style="background: #fef3c7; border: 2px solid #fde68a; border-radius: 16px; padding: 32px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 24px; font-size: 18px; color: #1f2937; font-weight: 600; text-align: center;">
                        ⭐ Paid By
                    </h3>
                    
                    <!-- Client Card -->
                    <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <img src="{client_profile_image}" alt="{client_name}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 3px solid #f59e0b; margin-right: 20px;">
                            <div>
                                <h4 style="margin: 0 0 8px; font-size: 20px; color: #1f2937; font-weight: 600;">
                                    {client_name}
                                </h4>
                                <div style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px; display: inline-block;">
                                    TASK POSTER
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Transaction Success Message -->
                <div style="background: #ecfdf5; border: 2px solid #a7f3d0; border-radius: 12px; padding: 24px; margin-bottom: 32px; text-align: center;">
                    <p style="margin: 0 0 12px; font-size: 18px; color: #065f46; font-weight: 600;">
                        🎉 Transaction Complete!
                    </p>
                    <p style="margin: 0; font-size: 14px; color: #047857; line-height: 1.6;">
                        Great job completing this task! {client_first_name} has confirmed your work and released the payment.<br>
                        Keep up the excellent work to earn more and build your reputation on duotasks.
                    </p>
                </div>
                
                <!-- Next Steps -->
                <div style="background: #eff6ff; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                    <h3 style="margin: 0 0 16px; font-size: 18px; color: #1f2937; font-weight: 600;">
                        💡 What You Can Do Next:
                    </h3>
                    <div style="color: #1e40af; line-height: 1.6; font-size: 14px;">
                        <p style="margin: 0 0 8px;">✅ Check your wallet balance to see your updated funds</p>
                        <p style="margin: 0 0 8px;">✅ Withdraw your earnings to M-PESA or your bank account</p>
                        <p style="margin: 0 0 8px;">✅ Browse available tasks to find your next opportunity</p>
                        <p style="margin: 0;">✅ Build your reputation by completing more tasks successfully</p>
                    </div>
                </div>
                
                <!-- Service Fee Info -->
                <div style="background: #f9fafb; border-left: 4px solid #6b7280; border-radius: 8px; padding: 20px; margin-bottom: 32px;">
                    <h4 style="margin: 0 0 12px; font-size: 14px; color: #1f2937; font-weight: 600;">
                        ℹ️ About the Service Fee
                    </h4>
                    <p style="margin: 0; font-size: 13px; color: #4b5563; line-height: 1.6;">
                        The 10% service fee helps us maintain the duotasks platform, provide customer support, secure payment processing, and ensure a safe marketplace for both task posters and doers. This fee is standard across all completed tasks.
                    </p>
                </div>
                
                <!-- Keep Earning Banner -->
                <div style="background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); border-radius: 16px; padding: 32px; text-align: center; box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);">
                    <h3 style="margin: 0 0 12px; font-size: 22px; color: #ffffff; font-weight: 700;">
                        Ready for More Tasks?
                    </h3>
                    <p style="margin: 0 0 24px; font-size: 15px; color: #dbeafe; line-height: 1.5;">
                        Browse available tasks and keep earning on duotasks
                    </p>
                    <a href="https://duotasks.net/tasks" style="display: inline-block; background: #ffffff; color: #1e40af; padding: 16px 40px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);">
                        Find More Tasks →
                    </a>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f9fafb; padding: 32px 40px; border-top: 1px solid #f0f0f0;">
                <div style="text-align: center;">
                    <img src="{favicon_logo}" alt="duotasks" style="height: 100px; width: auto; margin-bottom: 16px; opacity: 0.7;">
                    <p style="margin: 0 0 8px; font-size: 16px; color: #1f2937; font-weight: 600;">
                        duotasks
                    </p>
                    <p style="margin: 0 0 16px; font-size: 14px; color: #6b7280;">
                        Earn money, build your reputation
                    </p>
                    <div style="margin-bottom: 16px;">
                        <a href="https://duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Visit Website
                        </a>
                        <a href="https://duotasks.net/wallet" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            View Wallet
                        </a>
                        <a href="mailto:support@duotasks.net" style="color: #00915a; text-decoration: none; font-size: 14px; margin: 0 12px;">
                            Contact Support
                        </a>
                    </div>
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 16px;">
                        <p style="margin: 0; font-size: 12px; color: #9ca3af;">
                            © 2025 duotasks. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """